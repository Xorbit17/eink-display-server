from typing import (
    Tuple,
    Optional
)

from .pipeline_registry import ImageProcessingContext, pipeline_function
from PIL import Image
from pydantic import BaseModel


class ResizeCropParameters(BaseModel):
    resolution: Tuple[int, int]
    rotate: Optional[int] = 0


@pipeline_function("resize_crop", ResizeCropParameters)
def resize_crop(
    image: Image.Image,
    context: ImageProcessingContext,
    *,
    resolution: Tuple[int, int],
    rotate: int,
) -> Image.Image:
    target_w, target_h = resolution
    src_w, src_h = image.size

    scale = max(target_w / src_w, target_h / src_h)
    new_w, new_h = int(src_w * scale), int(src_h * scale)

    resized = image.resize((new_w, new_h), resample=Image.Resampling.LANCZOS)

    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    right = left + target_w
    bottom = top + target_h

    cropped = resized.crop((left, top, right, bottom))

    if (rotate):
        return cropped.rotate(rotate, expand=True)
    else:
        return cropped
