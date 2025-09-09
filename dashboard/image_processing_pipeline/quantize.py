from dashboard.color_constants import PaletteEnum
from .pipeline_registry import pipeline_function
from pydantic import BaseModel, field_validator, field_serializer
from PIL.Image import Image, new, Dither
from typing import Set, Any
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

    @field_validator("palette", mode="before")
    @classmethod
    def coerce_palette(cls, v: Any) -> PaletteEnum:
        if isinstance(v, PaletteEnum):
            return v
        if isinstance(v, str):
            try:
                return PaletteEnum[v]
            except KeyError:
                # Optional: try by label
                for m in PaletteEnum:
                    if getattr(m, "label", m.name).upper() == v:
                        return m
        raise ValueError(
            f"Invalid palette {v!r}. Valid: {[m.name for m in PaletteEnum]}"
        )

    @field_serializer("palette")
    def serialize_palette(self, p: PaletteEnum) -> str:
        return p.name

@pipeline_function("quantize",QuantizeParameters)
def quantize_to_palette(img, context, *, palette: PaletteEnum) -> Image:
    base = img.convert("RGB")
    pal = _build_P_mode_palette_image(palette.to_set())
    q = base.quantize(palette=pal, dither=Dither.NONE)  # P-mode
    return q.convert("RGB")
