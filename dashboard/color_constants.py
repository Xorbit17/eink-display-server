from typing import Any, Dict, Set, Tuple, TypeAlias, List
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

color: TypeAlias = Tuple[int,int,int]

def mix_color(*colors: color, weights: list[float] | None = None) -> color:
    if not colors:
        raise ValueError("At least one color must be provided.")

    if weights is None:
        weights = [1.0] * len(colors)
    if len(weights) != len(colors):
        raise ValueError("Length of weights must match number of colors.")

    total_weight = sum(weights)
    if total_weight == 0:
        raise ValueError("Sum of weights must not be zero.")

    r = sum(c[0] * w for c, w in zip(colors, weights)) / total_weight
    g = sum(c[1] * w for c, w in zip(colors, weights)) / total_weight
    b = sum(c[2] * w for c, w in zip(colors, weights)) / total_weight

    return (int(round(r)), int(round(g)), int(round(b)))

def shades(start: color, end: color, steps: int) -> List[color]:
    if steps < 1:
        return []

    result: List[color] = []
    for i in range(1, steps + 1):
        t = i / (steps + 1)  # normalized fraction (skip 0 and 1)
        r = round(start[0] + (end[0] - start[0]) * t)
        g = round(start[1] + (end[1] - start[1]) * t)
        b = round(start[2] + (end[2] - start[2]) * t)
        result.append((r, g, b))
    return result

# Native colors the e-ink screen is capable of
BLACK = (0,0,0)
WHITE = (0,0,0)
YELLOW = (208, 190, 71)
RED = (156, 72, 75)
BLUE = (61, 59, 94)
GREEN = (58, 91, 70)

NATIVE_COLORS = [
    BLACK, # -> 0
    WHITE, # -> 1
    YELLOW, # Yellow -> 2
    RED, # red -> 3
    BLUE, # Blue -> 5
    GREEN, # green -> 6
]

EXTENDED_COLORS = [
    mix_color(BLACK, WHITE), # Grey
    mix_color(YELLOW, RED), # Orange
    mix_color(RED, BLUE), # Purple
    mix_color(BLUE, GREEN) # Cyan
]

SKINTONES = [
    (255, 235, 220), # Pale
    (229, 194, 165), # Caucasian
    (170, 120, 90), # Brown
    (96, 70, 60) # Black
    ]

WOOD_COLORS = [
    (222, 184, 135),  # Pine (light beige-brown with yellow tone)
    (160, 82, 45),    # Oak (medium warm brown)
    (38, 26, 26),     # Ebony (very dark brown, almost black)
]

# Palette definitions

NATIVE_PALETTE = {
    "native": NATIVE_COLORS,
}

GRAYSCALE_PALETTE = {
    "grayscale": [
        BLACK,
        WHITE,
    ],
}

EXTENDED_PALETTE = {
    "native": NATIVE_COLORS,
    "extended": EXTENDED_COLORS,
}

# Seems problematic
SHADED_PALETTE = {
    "native": NATIVE_COLORS,
    "skin_tones": SKINTONES,
    "grayscale": shades(BLACK, WHITE,3),
    # Tints = mix with white at 0/25/50/75/100%
    "red_tints": shades(RED,WHITE,3) ,
    "green_tints": shades(GREEN,WHITE,3),
    "blue_tints": shades(BLUE,WHITE,3),
    # Shades = mix with black at 0/25/50/75/100%
    "red_shades": shades(RED,BLACK,3),
    "green_shades": shades(GREEN,BLACK,3),
    "blue_shades": shades(BLUE,BLACK,3),

}

NATIVE_WITH_SKIN_PALETTE = {
    "native": NATIVE_COLORS,
    "skin_tones": SKINTONES
}

EXTENDED_NATIVE_SKIN_PALETTE = {
    "native": NATIVE_COLORS,
    "extended": EXTENDED_COLORS,
    "skin_tones": SKINTONES,
}

WOODCUT_PALETTE = {
    "wood": WOOD_COLORS,
    "black_white": [BLACK, WHITE],
}

WOOD_EXTENDED_PALETTE = {
    "wood": WOOD_COLORS,
    "native": NATIVE_COLORS,
    "extended": EXTENDED_COLORS,
}

class PaletteEnum(LabeledEnum):
    NATIVE = (NATIVE_PALETTE, "Native")
    EXTENDED = (EXTENDED_PALETTE, "Extended")
    SHADED = (SHADED_PALETTE, "Shaded")
    NATIVE_WITH_SKIN = (NATIVE_WITH_SKIN_PALETTE, "Native + Skin Tones")
    EXTENDED_NATIVE_SKIN = (EXTENDED_NATIVE_SKIN_PALETTE, "Extended + Native + Skin Tones")
    GRAYSCALE = (GRAYSCALE_PALETTE, "Grayscale")
    WOODCUT = (WOODCUT_PALETTE, "Woodcut")
    WOOD_EXTENDED = (WOOD_EXTENDED_PALETTE, "Wood extended")
    
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
    
if __name__ == "__main__":
    for palette in PaletteEnum:
        print (f"{palette.name}:{palette.to_set()}") # type: ignore
    # TODO generate a test image
