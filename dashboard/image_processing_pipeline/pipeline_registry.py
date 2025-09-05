from enum import Enum
from typing import Dict, Any, Tuple, Type, Protocol, Iterable, TypeAlias
from dashboard.server_types import BaseLogger, ConsoleLogger
from pathlib import Path

from typing import Optional
from pydantic import BaseModel
from PIL.Image import Image, open
from dataclasses import dataclass
from io import BytesIO

from dashboard.services.openai_prompting import GenericImageClassification


class PipelineFunctionNotFoundException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class BadPipelineArgumentsException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ImageProcessingOutputEnum(Enum):
    BYTES = ("bytes", bytes)
    FILE = ("file", Path)

    @property
    def label(self) -> str: return self.value[0]

    @property
    def pytype(self) -> type: return self.value[1]


class ImageProcessingPipelineStep:
    name: str
    kwargs: dict[str, Any]

    def __init__(self,_name,**_kwargs):
        self.name = _name
        self.kwargs = _kwargs

ImageProcessingPipeline: TypeAlias = Iterable[ImageProcessingPipelineStep]

@dataclass
class ImageProcessingContext:
    pipeline: Iterable[ImageProcessingPipelineStep]
    current_step: int
    current_step_name: str
    current_step_arguments: Dict[str, Any]
    logger: BaseLogger
    classification: GenericImageClassification | None = None

class PipelineFunction(Protocol):
    def __call__(
        self,
        image: Image,
        context: ImageProcessingContext,
        /,
        *args: Any,
        **kwargs: Any,
    ) -> Image: ...


_registry: Dict[str, Tuple[PipelineFunction, Optional[Type[BaseModel]]]] = {}


def pipeline_function(name: str, param_model: Optional[Type[BaseModel]] = None):
    def deco(fn: PipelineFunction) -> PipelineFunction:
        def pipeline_function(
            image: Image, context: ImageProcessingContext, /, *args: Any, **kwargs: Any
        ) -> Image:
            if param_model:
                # Check
                validated_kwargs = param_model.model_validate(dict(**kwargs)).model_dump()
                result = fn(image, context, *args, **validated_kwargs)
                return result
            return fn(image, context, *args, **kwargs)

        _registry[name] = (pipeline_function, param_model)
        return pipeline_function

    return deco


def get_pipeline_function_and_model(name: str) -> Tuple[PipelineFunction, Type[BaseModel] | None]:
    result = _registry.get(name, None)
    if not result:
        available = ", ".join(sorted(_registry))
        raise PipelineFunctionNotFoundException(
            f"No pipeline function '{name}'. Available: [{available}]"
        )
    return result

def output_bytes(image: Image) -> BytesIO:
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def output_file(image: Image, output: Path | str) -> Path:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG")
    return output


@pipeline_function("noop")
def noop(image: Image, _) -> Image:
    return image

def default_to_image(input: Image | BytesIO | bytes) -> Image:
    if isinstance(input, Image):
        return input
    return open(input).convert("RGB")

class PipelineStepModel(BaseModel):
    name: str
    # any extra keys should go into kwargs
    class Config:
        extra = "allow"

def load_pipeline(data: list[dict[str, Any]]) -> list[ImageProcessingPipelineStep]:
    steps: list[ImageProcessingPipelineStep] = []
    for step_dict in data:
        name = step_dict.get("name")
        if not name:
            raise ValueError("Pipeline step missing 'name'")

        _, param_model = _registry.get(name, (None, None))
        kwargs = {k: v for k, v in step_dict.items() if k != "name"}

        if param_model:
            kwargs = param_model.model_validate(kwargs).model_dump()

        steps.append(ImageProcessingPipelineStep(name, kwargs=kwargs))
    return steps


def process(
    input: Image | BytesIO | bytes,
    pipeline: Iterable[ImageProcessingPipelineStep],
    *,
    output_format: ImageProcessingOutputEnum = ImageProcessingOutputEnum.BYTES,
    output_path: Path | None = None,
    classification: GenericImageClassification | None = None,
    logger: BaseLogger,
) -> BytesIO | Path:
    image=default_to_image(input)
    if output_format == ImageProcessingOutputEnum.FILE and not output_path:
        raise BadPipelineArgumentsException(
            "When output type is FILE keyword arg output_path must be provided"
        )

    for i, step in enumerate(pipeline):
        context = ImageProcessingContext(
            pipeline=pipeline,
            current_step=i,
            current_step_name=step.name,
            current_step_arguments=step.kwargs,
            logger=logger,
            classification=classification,
        )
        image = get_pipeline_function_and_model(step.name)[0](image, context, **step.kwargs)
    if output_format == ImageProcessingOutputEnum.FILE:
        return output_file(image, output_path)  # type: ignore
    if output_format == ImageProcessingOutputEnum.BYTES:
        return output_bytes(image)
    raise RuntimeError("Impossible code segment")
