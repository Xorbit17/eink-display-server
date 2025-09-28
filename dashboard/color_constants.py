from typing import Any, Dict, Set, Tuple, TypeAlias, List
from enum import Enum
from dashboard.constants import LabeledEnum
from dashboard.server_types import RGB
from PIL import Image, ImageDraw
from functools import cache
from re import sub

color: TypeAlias = Tuple[Tuple[int,int,int],str] | Tuple[Tuple[int,int,int],str, str]
PaletteDict: TypeAlias = Dict[str,List[color]]

def mix_color(*colors: color, weights: list[float] | None = None, name: str | None = None) -> color:
    if not colors:
        raise ValueError("At least one color must be provided.")

    if weights is None:
        weights = [1.0] * len(colors)
    if len(weights) != len(colors):
        raise ValueError("Length of weights must match number of colors.")

    total_weight = sum(weights)
    if total_weight == 0:
        raise ValueError("Sum of weights must not be zero.")

    r = sum(c[0][0] * w for c, w in zip(colors, weights)) / total_weight
    g = sum(c[0][1] * w for c, w in zip(colors, weights)) / total_weight
    b = sum(c[0][2] * w for c, w in zip(colors, weights)) / total_weight
    name = name if name else "-".join([x[1] for x in colors])
    return ((int(round(r)), int(round(g)), int(round(b))), name)

def shades(start: color, end: color, steps: int, base_name: str) -> List[color]:
    if steps < 1:
        return []

    result: List[color] = []
    for i in range(1, steps + 1):
        t = i / (steps + 1)  # normalized fraction (skip 0 and 1)
        r = round(start[0][0] + (end[0][0] - start[0][0]) * t)
        g = round(start[0][1] + (end[0][1] - start[0][1]) * t)
        b = round(start[0][2] + (end[0][2] - start[0][2]) * t)
        percent_shift = round(i * 100.0/(steps + 1))
        name = f"{base_name}-{percent_shift}"
        result.append(((r, g, b),name))
    return result

def extract_rgb_set(palette: Dict[str, List[color]], *, coerce_lists: bool = False) -> Set[Tuple[int, int, int]]:
    out: Set[Tuple[int, int, int]] = set()
    for _,v  in palette.items():
        for c in v:
            out.add(c[0])
    return out

def generate_tints_shades(base_color_list: List[color],steps=3) -> List[color]:
    result: List[color] = []
    for c in base_color_list:
        result = result + shades(c,WHITE,steps,base_name=f"{c[1]}-lighter")
        result = result + shades(c,BLACK,steps,base_name=f"{c[1]}-darker")
    return result


# Native colors the e-ink screen is capable of
BLACK: color =  ((0,0,0), "black")
WHITE: color =  ((255,255,255), "white")
YELLOW: color =  ((208, 190, 71), "yellow","eink-yellow")
RED: color =  ((156, 72, 75), "red","eink-red")
BLUE: color =  ((61, 59, 94), "blue","eink-blue")
GREEN: color =  ((58, 91, 70), "green","eink-green")

NATIVE_COLORS: List[color] = [
    BLACK ,       # -> 0
    WHITE,         # -> 1
    YELLOW,       # -> 2
    RED,             # -> 3
    BLUE,           # -> 4
    GREEN,         # -> 5
]

BASE_COLORS: List[color] = [
    YELLOW,       # -> 2
    RED,             # -> 3
    BLUE,           # -> 4
    GREEN,         # -> 5
]

# These colors look subjectively nice on the e-ink screen after dithering
EXTENDED_COLORS: List[color] = [
    mix_color(BLACK, WHITE, weights=[0.2, 0.8], name="light-grey"),
    mix_color(BLACK, WHITE, weights=[0.8, 0.2], name="dark-grey"),
    mix_color(BLACK, WHITE, weights=[0.5, 0.5], name="grey"),
    mix_color(YELLOW, RED, name="orange"),
    mix_color(RED, BLUE, name="purple"),
    mix_color(BLUE, GREEN, name="navy"),
    mix_color(BLUE, YELLOW, weights=[0.3, 0.7],name="dirty-yellow"),
    mix_color(BLUE, BLACK, WHITE, weights=[0.5, 0.3, 1.0], name="sky-blue"),
    mix_color(RED, GREEN, name="brown"),
]

EXTENDED_BASE_COLORS: List[color] = [
    mix_color(YELLOW, RED, name="orange"),
    mix_color(RED, BLUE, name="purple"),
    mix_color(BLUE, GREEN, name="navy"),
    mix_color(RED, GREEN, name="brown"),
]

SKINTONES: List[color] = [
    ((255, 235, 220), "skin-pale"),
    ((229, 194, 165), "skin-caucasian"),
    ((170, 120, 90), "skin-brown"),
    ((96, 70, 60), "skin-black"),
]

WOOD_COLORS: List[color] = [
    ((222, 184, 135), "wood-pine"),   # light beige-brown with yellow tone
    ((160, 82, 45), "wood-oak"),      # medium warm brown
    ((38, 26, 26), "wood-ebony"),     # very dark brown, almost black
]

# Palette definitions

NATIVE_PALETTE: PaletteDict = {
    "native": NATIVE_COLORS,
}

BLACK_WHITE_PALETTE: PaletteDict = {
    "black-white": [
        BLACK,
        WHITE,
    ],
}

EXTENDED_PALETTE: PaletteDict = {
    "native": NATIVE_COLORS,
    "extended": EXTENDED_COLORS,
}

NATIVE_SHADED_PALETTE: PaletteDict = {
    "native": NATIVE_COLORS,
    "grayscale": shades(WHITE, BLACK,3,base_name="grey"),
    "shades": generate_tints_shades(BASE_COLORS,3)
}
NATIVE_EXTENDED_SHADED_PALETTE: PaletteDict = {
    "native": NATIVE_COLORS,
    "extended": EXTENDED_COLORS,
    "grayscale": shades(WHITE, BLACK,3,base_name="grey"),
    "shades": generate_tints_shades(BASE_COLORS,3),
    "extended-shades": generate_tints_shades(EXTENDED_BASE_COLORS,3),
}
NATIVE_EXTENDED_SHADED_SKIN_PALETTE: PaletteDict = {
    "native": NATIVE_COLORS,
    "extended": EXTENDED_COLORS,
    "grayscale": shades(WHITE, BLACK,3,base_name="grey"),
    "shades": generate_tints_shades(BASE_COLORS,3),
    "extended-shades": generate_tints_shades(EXTENDED_BASE_COLORS,3),
    "skin_tones": SKINTONES,
}

NATIVE_SKIN_PALETTE: PaletteDict = {
    "native": NATIVE_COLORS,
    "skin_tones": SKINTONES,
}

NATIVE_SKIN_EXTENDED_PALETTE: PaletteDict = {
    "native": NATIVE_COLORS,
    "extended": EXTENDED_COLORS,
    "skin_tones": SKINTONES,
}

WOODCUT_PALETTE: PaletteDict = {
    "wood": WOOD_COLORS,
    "black_white": [BLACK, WHITE],
}

WOOD_EXTENDED_PALETTE: PaletteDict = {
    "wood": WOOD_COLORS,
    "native": NATIVE_COLORS,
    "extended": EXTENDED_COLORS,
}

def make_canvas(width: int = 1200, height: int = 1600, color: color = ((255, 255, 255), "white")) -> Image.Image:
    return Image.new("RGB", (width, height), color[0])

def draw_square(img: Image.Image, top_left: Tuple[int, int], size: int, color: color) -> None:
    draw = ImageDraw.Draw(img)
    x, y = top_left
    draw.rectangle([x, y, x + size, y + size], fill=color[0])

SWATCH_SIZE = 64

PALETTE_CHOICES = [
    ("NATIVE", "Native"),
    ("EXTENDED", "Extended"),
    ("NATIVE_SHADED", "Shaded"),
    ("NATIVE_EXTENDED_SHADED", "Shaded + Extended"),
    ("NATIVE_EXTENDED_SHADED_SKIN", "Shaded + Extended"),
    ("NATIVE_SKIN", "Native + Skin Tones"),
    ("NATIVE_SKIN_EXTENDED", "Extended + Native + Skin Tones"),
    ("BLACK_WHITE", "Black-white"),
    ("WOODCUT", "Woodcut"),
    ("WOOD_EXTENDED", "Wood extended"),
]

class PaletteEnum(LabeledEnum):
    NATIVE = (NATIVE_PALETTE, "Native")
    EXTENDED = (EXTENDED_PALETTE, "Extended")
    NATIVE_SHADED = (NATIVE_SHADED_PALETTE, "Shaded")
    NATIVE_EXTENDED_SHADED = (NATIVE_EXTENDED_SHADED_PALETTE, "Shaded + Extended")
    NATIVE_EXTENDED_SHADED_SKIN = (NATIVE_EXTENDED_SHADED_SKIN_PALETTE, "Shaded + Extended")
    NATIVE_SKIN = (NATIVE_SKIN_PALETTE, "Native + Skin Tones")
    NATIVE_SKIN_EXTENDED = (NATIVE_SKIN_EXTENDED_PALETTE, "Extended + Native + Skin Tones")
    BLACK_WHITE = (BLACK_WHITE_PALETTE, "Black-white")
    WOODCUT = (WOODCUT_PALETTE, "Woodcut")
    WOOD_EXTENDED = (WOOD_EXTENDED_PALETTE, "Wood extended")
    
    def to_set(self) -> Set[RGB]:
        """Return this palette as a set of RGB tuples."""
        return extract_rgb_set(self.value)

    @cache
    def make_color_swatch_image(self, canvas_res: tuple[int,int] | None = None) -> Image.Image:
        palette_dict = self.value
        if canvas_res is not None:
            canvas = make_canvas()
            rows = len(palette_dict)
            columns = max([len(palette_dict[key]) for key in palette_dict])
            size = min(1200 // columns, 1600 // rows)
        else:
            size = SWATCH_SIZE
            rows = len(palette_dict)
            columns = max([len(palette_dict[key]) for key in palette_dict])
            canvas = make_canvas(columns * size, rows * size)
        
        cursor = (0,0)
        for k,v in palette_dict.items():
            for c in v:
                draw_square(canvas, cursor,size,c)
                cursor = (cursor[0] + size, cursor[1])
            cursor = (0, cursor[1]+size)
        
        return canvas
    
    def to_css_vars(self) -> str:
        out_lines = [":root {"]
        for _,v in self.value.items():
            for c in v:
                css_name = c[2] if len(c) == 3 else sub(r"\s+","-", c[1].lower())
                out_lines.append(f"    --{css_name}: rgb({c[0][0]},{c[0][1]},{c[0][2]});")
        out_lines.append("}\n")
        return "\n".join(out_lines)

    @classmethod
    def get_color_set(cls, name: str) -> Set[RGB]:
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
    # from pathlib import Path
    # for palette in PaletteEnum:
    #     filename = Path("/home/dv/Documents/eink-display-server/tests/colors") / f"color_swatch_{palette.name}.png"
    #     palette.make_color_swatch_image().save(filename)
    print(PaletteEnum.NATIVE_EXTENDED_SHADED.to_css_vars())
