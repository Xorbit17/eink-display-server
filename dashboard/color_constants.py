from typing import Any, Dict, Set, Tuple
from enum import Enum
from dashboard.constants import LabeledEnum
from dashboard.server_types import RGB

def extract_rgb_set(palette: Dict[str, Any], *, coerce_lists: bool = False) -> Set[Tuple[int, int, int]]:
    out: Set[Tuple[int, int, int]] = set()

    def walk(x: Any) -> None:
        # exact tuples of length 3
        if isinstance(x, tuple) and len(x) == 3 and all(isinstance(c, int) for c in x):
            out.add(x)
            return
        if coerce_lists and isinstance(x, list) and len(x) == 3 and all(isinstance(c, int) for c in x):
            out.add(tuple(x))
            return
        if isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, (list, tuple, set)):
            for v in x:
                walk(v)

    walk(palette)
    return out

NATIVE_COLORS = [
    (0, 0, 0), # black
    (161, 164, 165), # grey
    (208, 190, 71), # Yellow
    (156, 72, 75), # red
    (61, 59, 94), # Blue
    (58, 91, 70), # green
    (255, 255, 255) # white
]
EXTENDED_COLORS = [
    # --- Greyscale ---
    (81, 82, 83),      # dark grey
    (208, 210, 210),   # light grey
    (242, 242, 242),    # very light grey

    # --- Yellow variants ---
    (120, 110, 40),    # dark yellow / ochre
    (240, 220, 130),   # light yellow

    # --- Red variants ---
    (109, 66, 85),     # dark red / purple-red
    (200, 120, 120),   # light red / pinkish

    # --- Blue variants ---
    (30, 30, 60),      # dark blue / navy
    (158, 157, 175),   # light blue

    # --- Green variants ---
    (40, 65, 50),      # dark green / forest
    (100, 140, 110),   # light green / sage

    # --- Orange / Purple extras ---
    (128, 118, 110),   # orange / brownish orange
    (170, 120, 60),    # brighter orange
    (120, 90, 150),    # purple
]

GREYSCALE_COLORS = [
        (0, 0, 0),
        (32, 32, 32),
        (64, 64, 64),
        (96, 96, 96),
        (128, 128, 128),
        (160, 160, 160),
        (192, 192, 192),
        (224, 224, 224),
        (255, 255, 255),
]

RED_TINTS = [
        (255, 0, 0), (255, 64, 64), (255, 128, 128), (255, 191, 191), (255, 255, 255)
    ]
GREEN_TINTS = [
        (0, 255, 0), (64, 255, 64), (128, 255, 128), (191, 255, 191), (255, 255, 255)
    ]
BLUE_TINTS = [
        (0, 0, 255), (64, 64, 255), (128, 128, 255), (191, 191, 255), (255, 255, 255)
    ]
RED_SHADES = [
        (255, 0, 0), (191, 0, 0), (128, 0, 0), (64, 0, 0), (0, 0, 0)
    ]
GREEN_SHADES =[
        (0, 255, 0), (0, 191, 0), (0, 128, 0), (0, 64, 0), (0, 0, 0)
    ]
BLUE_SHADES =[
        (0, 0, 255), (0, 0, 191), (0, 0, 128), (0, 0, 64), (0, 0, 0)
    ]
SKINTONES = [
    (255, 235, 220), # Pale
    (229, 194, 165), # Caucasian
    (170, 120, 90), # Brown
    (96, 70, 60) # Black
    ]

NATIVE_PALETTE = {
    "native": NATIVE_COLORS,
}

EXTENDED_PALETTE = {
    "native": NATIVE_COLORS,
    "extended": EXTENDED_COLORS,
}

SHADED_PALETTE = {
    "native": NATIVE_COLORS,
    "grayscale": GREYSCALE_COLORS,
    # Tints = mix with white at 0/25/50/75/100%
    "red_tints": RED_TINTS ,
    "green_tints": GREEN_TINTS,
    "blue_tints": BLUE_TINTS,
    # Shades = mix with black at 0/25/50/75/100%
    "red_shades": RED_SHADES,
    "green_shades": GREEN_SHADES,
    "blue_shades": BLUE_SHADES,
    "skin_tones": SKINTONES
}

NATIVE_WITH_SKIN_PALETTE = {
    "native": NATIVE_COLORS,
    "grayscale": GREYSCALE_COLORS,
    "skin_tones": SKINTONES
}

EXTENDED_NATIVE_SKIN_PALETTE = {
    "native": NATIVE_COLORS,
    "extended": EXTENDED_COLORS,
    "grayscale": GREYSCALE_COLORS,
    "skin_tones": SKINTONES,
}

class PaletteEnum(LabeledEnum):
    NATIVE = (NATIVE_PALETTE, "Native")
    EXTENDED = (EXTENDED_PALETTE, "Extended")
    SHADED = (SHADED_PALETTE, "Shaded")
    NATIVE_WITH_SKIN = (NATIVE_WITH_SKIN_PALETTE, "Native + Skin Tones")
    EXTENDED_NATIVE_SKIN = (EXTENDED_NATIVE_SKIN_PALETTE, "Extended + Native + Skin Tones")

    def to_set(self) -> Set[RGB]:
        """Return this palette as a set of RGB tuples."""
        return extract_rgb_set(self.value)

    @classmethod
    def get(cls, name: str) -> Set[RGB]:
        """
        Retrieve a palette set by enum key (case-insensitive).
        
        Example:
            PaletteEnum.get("native") -> { (0,0,0), (255,255,255), ... }
        """
        try:
            member = cls[name.upper()]
        except KeyError:
            raise ValueError(f"Unknown palette '{name}'. Valid options: {[m.name for m in cls]}")
        return member.to_set()
    
