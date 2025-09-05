from dashboard.color_constants import PaletteEnum
from .pipeline_registry import pipeline_function
from pydantic import BaseModel
from PIL.Image import Image, new, Dither
from typing import Set
from dashboard.server_types import RGB


def _build_P_mode_palette_image(colors: Set[RGB]) -> Image:
    if len(colors) > 256:
        raise ValueError("Pillow palettes support max 256 colors.")
    flat = []
    for r, g, b in colors:
        flat.extend([int(r), int(g), int(b)])
    while len(flat) < 256 * 3:
        flat.extend([0, 0, 0])
    pal = new("P", (1, 1))
    pal.putpalette(flat)
    return pal

class QuantizeParameters(BaseModel):
    palette: PaletteEnum

@pipeline_function("quantize",QuantizeParameters)
def quantize_to_palette(img, context, *, palette: PaletteEnum) -> Image:
    base = img.convert("RGB")
    pal = _build_P_mode_palette_image(palette.to_set())
    q = base.quantize(palette=pal, dither=Dither.NONE)  # P-mode
    return q.convert("RGB")
