from pathlib import Path
import numpy as np
from django.utils.dateformat import time_format
from django.utils import timezone
from dashboard.color_constants import PaletteEnum
from dashboard.services.app_settings import settings
from .pipeline_registry import pipeline_function
from pydantic import BaseModel, field_validator, field_serializer
from PIL.Image import Image, new, Dither, blend, composite, Quantize
from PIL import ImageEnhance, ImageOps, ImageFilter
from typing import Set, Any, Optional
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
    dither: Optional[bool] = True

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
    
def save_debug(img: Image, suffix = ""):
    now = timezone.now()
    output_path = (
        Path(settings().image_generation_dir).resolve()
        / "bootscreens"
        / f"bootscreen_quant_{now.strftime('%Y%m%d%H%M%S')}{suffix}.png"
    )
    img.save(output_path)

def lut_bimodal(
    black_clip: int = 24,     # 0..255 range snapped to black
    white_clip: int = 24,     # 255-white_clip..255 snapped to white
    mid_gamma: float = 2.2,   # steepness of the mid S-curve (>=1)
    in_gamma: float = 2.2,    # approximate sRGB gamma in
    out_gamma: float = 2.2,   # approximate sRGB gamma out
) -> list[int]:
    """
    Returns a 256-entry LUT that snaps shadows/highlights and steepens midtones.
    Designed to crisp up black-on-white UI text before palette quantization.
    """
    lut = []
    for v in range(256):
        # Hard snap zones (in linear)
        if v <= black_clip:
            y = 0.0
        elif v >= 255 - white_clip:
            y = 1.0
        else:
            # Remap midtones with an S-curve (gamma-like)
            # Map the remaining range to 0..1
            t = (v - black_clip) / max(1, (255 - black_clip - white_clip))
            # Center around 0.5 to create symmetric S-curve
            # Use a simple gamma on both sides of the midpoint for “bimodal” pull
            if t < 0.5:
                t2 = 0.5 * (2 * t) ** (1.0 / mid_gamma)
            else:
                t2 = 1.0 - 0.5 * (2 * (1.0 - t)) ** (1.0 / mid_gamma)
            y = t2  # already in 0..1 midrange

        # 4) De-linearize
        o = int(round((y ** out_gamma) * 255.0))
        lut.append(max(0, min(255, o)))
    return lut

def lut_binary_threshold(t: int, low: int = 0, high: int = 255) -> list[int]:
    t = max(0, min(255, t))
    return [low] * (t + 1) + [high] * (255 - t)

def lut_ramp(lo: int, hi: int, low: int = 0, high: int = 255) -> list[int]:
    """Piecewise linear: <=lo→low, >=hi→high, between→linear ramp."""
    lo, hi = max(0, lo), min(255, hi)
    if hi <= lo:
        return [high] * 256  # degenerate case
    out = []
    for v in range(256):
        if v <= lo: y = low
        elif v >= hi: y = high
        else:
            y = low + (high - low) * (v - lo) / (hi - lo)
        out.append(int(round(y)))
    return out

def lut_invert(lut: list[int]) -> list[int]:
    return [255 - v for v in lut]

def _srgb_to_linear(u):  # u in [0..1]
    return np.where(u <= 0.04045, u/12.92, ((u+0.055)/1.055)**2.4)

def _linear_to_srgb(u):
    return np.where(u <= 0.0031308, 12.92*u, 1.055*(u**(1/2.4)) - 0.055)

@pipeline_function("quantize", QuantizeParameters)
def quantize_to_palette(img, context, *, palette: PaletteEnum, dither: bool) -> Image:
    context.logger.info(f"Quantizing to palette: {palette.name} with dither option {'ON' if dither else 'OFF'}")
    result = img.convert('RGB')
    pal_image = _build_P_mode_palette_image(palette.to_set())
    dither_mode = Dither.FLOYDSTEINBERG if dither else Dither.NONE
    result = result.quantize(palette=pal_image, dither=dither_mode, method=dither_mode).convert("RGB")
    return result

@pipeline_function("p_mode_eink_optimize", None)
def p_mode_eink_optimize(img, context) -> Image:
    context.logger.info("Converting image to e-ink ready format")
    result = img.convert('RGB')
    pal_image = _build_P_mode_palette_image(PaletteEnum.NATIVE.to_set())
    result = result.quantize(palette=pal_image, dither=Dither.FLOYDSTEINBERG)
    result = result.convert('P')
    return result
    