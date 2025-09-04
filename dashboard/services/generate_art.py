from typing import Dict, Iterable, List, Sequence, Tuple, Optional, Union, Protocol, cast
from PIL import Image
from pathlib import Path
from django.template import Context, Template
from dashboard.services.openai import openai_client
from dashboard.services.image_processing import pil_to_base64, base64_to_pil
from dashboard.jobs.image_processing_declaration import ART_STYLE_CHOICES, CONTENT_TYPE_MARKDOWN, CONTENT_TYPE_CLASSIFICATION_CHOICES, PipelineArgs, PipelineSteps, ArtStyle
from typing import Any, Callable, Iterable, List, Optional, Sequence, Tuple
from dataclasses import dataclass, field
from pydantic import BaseModel
from PIL import Image
from dashboard.services.classify_image import ImageClassification
from io import BytesIO

RGB = Tuple[int, int, int]
ART_GENERATOR_PROMPT_TEMPLATE = Template(
    (
        Path(__file__).resolve().parent.parent
        / "context_templates"
        / "image-artstyle-applicator.md"
    ).read_text(),
)

class Logger(Protocol):
    def debug(self, msg, **ctx) -> None: ...
    def info(self, msg, **ctx) -> None: ...
    def warn(self, msg, **ctx) -> None: ...
    def error(self, msg, **ctx) -> None: ...

class ConsoleLogger:
    def debug(self, msg: str, **ctx: Any) -> None:
        print(f"[DEBUG] {msg}", ctx if ctx else "")

    def info(self, msg: str, **ctx: Any) -> None:
        print(f"[INFO] {msg}", ctx if ctx else "")

    def warn(self, msg: str, **ctx: Any) -> None:
        print(f"[WARN] {msg}", ctx if ctx else "")

    def error(self, msg: str, **ctx: Any) -> None:
        print(f"[ERROR] {msg}", ctx if ctx else "")

default_logger: Logger = ConsoleLogger()

@dataclass
class ImageProcessingContext:
    classification: ImageClassification | None = None
    art_style: ArtStyle = "KEEP_PHOTO"
    pipeline: PipelineSteps = field(default_factory=list)
    pipeline_args: PipelineArgs = field(default_factory=list)
    current_arguments: Any = None
    current_step: int = 0
    logger: Logger = default_logger


def get_art_generator_prompt(context: dict) -> str:
    return ART_GENERATOR_PROMPT_TEMPLATE.render(Context(context))

def get_art_instructions_prompt(markdown, *, context: ImageProcessingContext):
    base_dir = Path(__file__).resolve().parent
    md_path = base_dir / "context-templates" / "artstyles" / markdown
    if (md_path.exists()):
        return md_path.read_text()
    art_style_readable = next(t[1] for t in ART_STYLE_CHOICES if t[0]==context.art_style)
    return art_style_readable

def get_content_type_instructions(*, context: ImageProcessingContext):
    if not context.classification:
        return RuntimeError("Classification not in context")
    markdown = CONTENT_TYPE_MARKDOWN.get(context.classification.contentType)
    if not markdown:
        raise RuntimeError()
    
    base_dir = Path(__file__).resolve().parent.parent
    md_path = base_dir / "context-templates" / "subject-types" / markdown
    if (md_path.exists()):
        return md_path.read_text()
    content_type_readable = next(t[1] for t in CONTENT_TYPE_CLASSIFICATION_CHOICES if t[0]==context.classification.contentType)
    return content_type_readable

# Pipeline function
def openai_process(
    image: Image.Image, markdown_filename, *, context: ImageProcessingContext
) -> Image.Image:
    if not context.classification:
        raise Exception("Context does not contain classification")
    instructions = get_art_instructions_prompt(
        markdown_filename, context=context
    )
    prompt = get_art_generator_prompt(
        context={
            "artstyle_instructions": instructions,
            "aspect_ratio": "portrait",
            "subject_type_instructions": get_content_type_instructions(context=context),
            "subject_type": context.classification.contentType,
            "art_style": context.art_style,
        }
    )

    has_alpha = image.mode in ("RGBA", "LA", "P") and (
        "A" in image.getbands() or "transparency" in image.info
    )
    if has_alpha:
        fmt, mime, img_to_send = "PNG", "image/png", image
    else:
        fmt, mime, img_to_send = "JPEG", "image/jpeg", image.convert("RGB")

    b64 = pil_to_base64(img_to_send, format=fmt)

    # TODO error handling?
    response = openai_client.responses.create(
        model="gpt-5",
        stream=False,
        tools=[{"type": "image_generation"}],
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": f"data:{mime};base64,{b64}",
                        "detail": "high",
                    },
                ],
            }
        ],
    )
    image_data = [
        output.result
        for output in response.output
        if output.type == "image_generation_call"
    ]
    if image_data[0]:
        return base64_to_pil(image_data[0])
    
    raise Exception("OpenAI did not return an image format")

# Pipeline function
def resize_crop(image: Image.Image, resolution: Tuple[int,int] | None, *, context: ImageProcessingContext) -> Image.Image:
    defaulted_resolution = (1200,1600) if resolution is None else resolution
    target_w, target_h = defaulted_resolution
    src_w, src_h = image.size

    scale = max(target_w / src_w, target_h / src_h)
    new_w, new_h = int(src_w * scale), int(src_h * scale)

    resized = image.resize((new_w, new_h), resample=Image.Resampling.LANCZOS)

    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    right = left + target_w
    bottom = top + target_h

    return resized.crop((left, top, right, bottom))

# Pipeline function
def output_bytes(
    image: Image.Image, format: str, *, context: dict
) -> BytesIO:
    buffer = BytesIO()
    fmt = format.lstrip(".").upper()  # TODO: validation
    image.save(buffer, format=fmt)
    buffer.seek(0)
    return buffer

# Pipeline function
def output_image(
    image: Image.Image, output: Path | str, format: str, *, context: dict
) -> Path:
    output = Path(output)
    fmt = format.lstrip(".").upper()  # TODO: validation
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format=fmt)
    return output


def noop(image: Image.Image) -> Image.Image:
    return image


def build_palette_list(
    palette: Dict[str, Iterable[Iterable[int]]],
    key_priority: Optional[Sequence[str]] = None,
    max_colors: Optional[int] = None,
) -> List[RGB]:
    seen = set()
    out: List[RGB] = []

    def emit(seq: Iterable[Iterable[int]]):
        for v in seq:
            if isinstance(v, (list, tuple)) and len(v) == 3:
                rgb = (int(v[0]), int(v[1]), int(v[2]))
                if rgb not in seen:
                    seen.add(rgb)
                    out.append(rgb)

    if key_priority:
        for k in key_priority:
            if k in palette:
                emit(palette[k])

    for k, seq in palette.items():
        if not key_priority or k not in key_priority:
            emit(seq)

    if max_colors is not None:
        return out[:max_colors]
    return out


def _build_P_mode_palette_image(colors: Sequence[RGB]) -> Image.Image:
    if len(colors) > 256:
        raise ValueError("Pillow palettes support max 256 colors.")
    flat = []
    for r, g, b in colors:
        flat.extend([int(r), int(g), int(b)])
    while len(flat) < 256 * 3:
        flat.extend([0, 0, 0])
    pal = Image.new("P", (1, 1))
    pal.putpalette(flat)
    return pal

# Pipeline function
def quantize_to_palette(img: Image.Image, colors: Sequence[RGB], *, context: Dict) -> Image.Image:
    """
    Remap `img` to `colors` using Pillow's fixed-palette quantizer (no dithering),
    then convert back to RGB. Keeps everything crisp and returns RGB.
    """
    if not isinstance(img, Image.Image):
        raise TypeError("img must be a PIL.Image.Image")

    base = img.convert("RGB")
    pal = _build_P_mode_palette_image(colors)
    q = base.quantize(palette=pal, dither=Image.Dither.NONE)  # P-mode
    return q.convert("RGB")


class PipelineError(RuntimeError):
    """Raised when a pipeline step fails or returns an invalid result."""
    pass


StepFn = Callable[..., Image.Image]
FinishFn = Callable[..., None]

# openai_process, resize_crop, quantize_to_palette, output_image
PIPELINE_FUNCTIONS: Dict[str,Callable] = {
    "openai_process": openai_process,
    "resize_crop": resize_crop,
    "quantize_to_palette": quantize_to_palette,
    "output_image": output_image,
    "output_bytes": output_bytes,
}

def get_pipeline_function(functionName: str) -> Callable:
    result = PIPELINE_FUNCTIONS.get(functionName)
    if not result:
        raise RuntimeError(f"Non existant pipeline function {functionName}")
    return result


def run_art_generation_pipeline(
    input: Union[Path, str, bytes],
    *,
    context: ImageProcessingContext,
) -> None:
    """
    Execute an image-processing pipeline.

    - Loads the input image first.
    - Runs all steps except the last sequentially, each returning a new Image.Image.
    - Calls the final step separately; it must save to `output` and return None.

    Conventions:
    - Every non-final step has signature: step(img: Image.Image, *args, context: dict) -> Image.Image
    - Final step has signature: final_step(img: Image.Image, output_path: Union[Path, str], *args, context: dict) -> None
    - `pipeline_args[i]` supplies the positional args tuple for `pipeline[i]` (excluding `img`, `context`, and for the
      final step also excluding `output_path`, which is injected here).
    """
    def _get_PIL(input: Union[Path, str, bytes]):
        if isinstance(input, bytes):
            with BytesIO(input) as bytebuyffer:
                img = Image.open(bytebuyffer)
                img.load()
            return img
        in_path = Path(cast(Union[str, Path], input))
        return Image.open(in_path)

    img = _get_PIL(input)

    if not context.pipeline:
        raise ValueError(
            "pipeline must contain at least one step"
        )

    # Run all intermediate steps
    for i, (step, args) in enumerate(zip(context.pipeline[:-1], context.pipeline_args[:-1])):
        if args is None:
            args = ()
        elif not isinstance(args, (tuple, list)):
            args = (args,)
        context.logger.debug(f"Executing step {i+1} of pipeline: {step}")
        context.current_arguments = context.pipeline_args[i]
        try:
            img = get_pipeline_function(step)(img, *context.current_arguments, context=context)
            context.logger.debug(f"Successfully completed  step {i} of pipeline")
        except Exception as e:
            context.logger.error(f"Step {i} of pipeline FAILED with error: {str(e)}")
            raise

    # Run the final (saving) step
    final_step = context.pipeline[-1]
    final_step_i = len(context.pipeline)
    final_args = () if not context.pipeline_args else context.pipeline_args[-1]
    if final_args is None:
        final_args = () 
    elif not isinstance(final_args, (tuple, list)):
        final_args = (final_args,)
    try:
        context.logger.debug(f"Executing final step {final_step_i} (saving) of pipeline")
        result = get_pipeline_function(final_step)(img, *final_args, context=context)
        context.logger.debug(f"Successfully completed  final step {final_step_i} (saving) of pipeline")
        return result
    except Exception as e:
        context.logger.error(f"Last step {final_step_i} (saving) of pipeline FAILED with error: {str(e)}")
        raise
