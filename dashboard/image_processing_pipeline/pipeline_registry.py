from __future__ import annotations
from importlib import import_module
import pkgutil
from enum import Enum
from typing import Dict, Any, Tuple, Type, Protocol, Iterable, Mapping, TypeAlias
from dashboard.server_types import BaseLogger, ConsoleLogger
from dashboard.services.app_settings import settings
from pathlib import Path
from django.conf import settings as django_settings
from django.utils import timezone
from typing import Optional
from pydantic import BaseModel, ValidationError
from PIL.Image import Image, open
from dataclasses import dataclass, field
from io import BytesIO
import json
from pathlib import Path
from datetime import datetime


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



@dataclass(init=False)
class ImageProcessingPipelineStep:
    name: str
    kwargs: dict[str, Any] = field(default_factory=dict)

    def __init__(self, name: str, **kwargs: Any):
        self.name = name
        self.kwargs = kwargs

    def _param_model(self) -> Optional[Type[BaseModel]]:
        load_all()
        _, model = get_pipeline_function_and_model(self.name)
        return model

    def to_dict(self) -> dict[str, Any]:
        model = self._param_model()
        if model is None:
            return {"name": self.name, **self.kwargs}

        try:
            m = model.model_validate(self.kwargs)
        except ValidationError as e:
            raise ValueError(f"[{self.name}] parameters failed validation: {e}") from e

        params_json = m.model_dump()
        return {"name": self.name, **params_json}

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ImageProcessingPipelineStep":
        name = data["name"]
        params = {k: v for k, v in data.items() if k != "name"}

        load_all()
        try:
            _, model = get_pipeline_function_and_model(name)
        except Exception:
            model = None

        if model is None:
            return cls(name, **params)

        try:
            m = model.model_validate(params)
        except ValidationError as e:
            raise ValueError(f"[{name}] parameters failed validation: {e}") from e

        field_names = type(m).model_fields.keys()
        native_params = {name: getattr(m, name) for name in field_names}
        return cls(name, **native_params)
    
ImageProcessingPipeline: TypeAlias = Iterable[ImageProcessingPipelineStep]

@dataclass
class ImageProcessingContext:
    pipeline: Iterable[ImageProcessingPipelineStep]
    current_step: int
    current_step_name: str
    current_step_arguments: Dict[str, Any]
    logger: BaseLogger
    invocation_start_time: datetime
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

_registry: Dict[str, Tuple[PipelineFunction, Optional[Type[BaseModel]]]] = {}
_LOADED = False

def pipeline_function(name: str, param_model: Optional[Type[BaseModel]] = None):
    def deco(fn: PipelineFunction) -> PipelineFunction:
        def pipeline_function(
            image: Image, context: ImageProcessingContext, /, *args: Any, **kwargs: Any
        ) -> Image:
            if param_model:
                # Validate parameters and preserve native Python types (e.g. enums)
                validated_model = param_model.model_validate(dict(**kwargs))
                validated_kwargs = {
                    field: getattr(validated_model, field)
                    for field in validated_model.__class__.model_fields.keys()
                }
                result = fn(image, context, *args, **validated_kwargs)
                return result
            return fn(image, context, *args, **kwargs)

        _registry[name] = (pipeline_function, param_model)
        return pipeline_function

    return deco

def _iter_submodules(package: str):
    pkg = import_module(package)
    for modinfo in pkgutil.iter_modules(pkg.__path__, package + "."):
        yield modinfo.name
        
def load_all(package: str = "dashboard.image_processing_pipeline") -> None:
    global _LOADED
    if _LOADED:
        return
    for fullname in _iter_submodules(package):
        import_module(fullname)  # importing triggers decorators
    _LOADED = True

@pipeline_function("noop")
def noop(image: Image, _) -> Image:
    return image

#Public API
class PipelineJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ImageProcessingPipelineStep):
            return o.to_dict()
        return super().default(o)

def pipeline_object_hook(obj):
    if "name" in obj and any(k for k in obj.keys() if k != "name"):
        return ImageProcessingPipelineStep.from_dict(obj)
    return obj

def pipeline_to_jsonable(p: Iterable[ImageProcessingPipelineStep]) -> list[dict[str, Any]]:
    return [step.to_dict() for step in p]

def pipeline_from_jsonable(data: list[dict[str, Any]]) -> list[ImageProcessingPipelineStep]:
    return [ImageProcessingPipelineStep.from_dict(d) for d in data]

def load_pipeline(data: list[dict[str, Any]]) -> list[ImageProcessingPipelineStep]:
    """
    Accepts JSON-like data (list of dicts), validates kwargs per step (if a
    Pydantic model is registered), and returns a list of Step objects.
    """
    load_all()
    steps_json: list[dict[str, Any]] = []

    for raw in data:
        name = raw.get("name")
        if not name:
            raise ValueError("Pipeline step missing 'name'")

        # Split name/params
        params = {k: v for k, v in raw.items() if k != "name"}

        # Optional Pydantic validation (normalize values)
        _, param_model = _registry.get(name, (None, None))
        if param_model:
            params = param_model.model_validate(params).model_dump()

        steps_json.append({"name": name, **params})

    # Convert JSONable dicts -> Step objects
    return pipeline_from_jsonable(steps_json)


def dump_pipeline(steps: list[ImageProcessingPipelineStep]) -> list[dict[str, Any]]:
    """
    Converts a list of Step objects into JSON-serializable dicts.
    Use this before saving into a JSONField.
    """
    load_all()
    return pipeline_to_jsonable(steps)


def get_pipeline_function_and_model(name: str) -> Tuple[PipelineFunction, Type[BaseModel] | None]:
    load_all()
    result = _registry.get(name, None)
    if not result:
        available = ", ".join(sorted(_registry))
        raise PipelineFunctionNotFoundException(
            f"No pipeline function '{name}'. Available: [{available}]"
        )
    return result

def get_pipeline_function(name: str) -> PipelineFunction:
    load_all()
    return get_pipeline_function_and_model(name)[0]


def _default_to_image(input: Image | BytesIO | bytes | Path) -> Image:
    if isinstance(input, Image):
        return input
    if isinstance(input, bytes):
        input = BytesIO(input)
    
    return open(input).convert("RGB")

def process(
    input: Image | BytesIO | bytes | Path,
    pipeline: Iterable[ImageProcessingPipelineStep],
    *,
    output_format: ImageProcessingOutputEnum | None = None,
    output_path: Path | None = None,
    classification: GenericImageClassification | None = None,
    logger: BaseLogger | None = None,
):
    load_all()
    image=_default_to_image(input)
    if not logger:
        logger = ConsoleLogger()
    if output_format == ImageProcessingOutputEnum.FILE and not output_path:
        raise BadPipelineArgumentsException(
            "When output type is FILE keyword arg output_path must be provided"
        )
    if output_path and not output_format:
        output_format = ImageProcessingOutputEnum.FILE
    if not output_path and not output_format:
        output_format = ImageProcessingOutputEnum.BYTES
    if output_path and output_format == ImageProcessingOutputEnum.BYTES:
        logger.warn("Something weird is going on. Output path was specified and output type is bytes (no file output)")
    now = timezone.now()
    now_file_str = now.strftime("%Y%m%d%H%M%S")
    for i, step in enumerate(pipeline):
        context = ImageProcessingContext(
            pipeline=pipeline,
            current_step=i,
            current_step_name=step.name,
            current_step_arguments=step.kwargs,
            logger=logger,
            invocation_start_time=now,
            classification=classification,
        )
        image = get_pipeline_function_and_model(step.name)[0](image, context, **step.kwargs)
        if django_settings.DEBUG:
            out_dir = Path(settings().image_generation_dir) / "pipeline_debug" / f"invocation_{now_file_str}"
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"step_{i}.png"
            image.save(out_path)

    if output_format == ImageProcessingOutputEnum.FILE:
        return output_file(image, output_path)  # type: ignore
    if output_format == ImageProcessingOutputEnum.BYTES:
        return output_bytes(image)
    raise RuntimeError("Impossible code segment")
