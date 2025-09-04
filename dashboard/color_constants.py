from typing import Any, Dict, Set, Tuple

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

NATIVE_PALETTE = {
    "native": NATIVE_COLORS,
}

NATIVE_PALETTE_SET = extract_rgb_set(NATIVE_PALETTE)

EXTENDED_PALETTE = {
    "native": NATIVE_COLORS,
    "extended": EXTENDED_COLORS,
}
EXTENDED_PALETTE_SET = extract_rgb_set(EXTENDED_PALETTE)


SHADED_PALETTE = {
    "native": NATIVE_COLORS,

    # Neutral greys (helpful for cleaner dithers on faces & text)
    "grayscale": [
        (0, 0, 0),
        (32, 32, 32),
        (64, 64, 64),
        (96, 96, 96),
        (128, 128, 128),
        (160, 160, 160),
        (192, 192, 192),
        (224, 224, 224),
        (255, 255, 255),
    ],

    # Basic/common extras (nice targets for quantization; your panel will dither toward R/Y/B/W)
    "basic": [
        (255, 165, 0),   # orange
        (255, 105, 180), # pink
        (255, 0, 255),   # magenta
        (0, 255, 255),   # cyan
        (128, 0, 128),   # purple
        (0, 128, 128),   # teal
        (139, 69, 19),   # saddle brown
        (128, 128, 0),   # olive
        (0, 0, 128),     # navy
        (128, 0, 0),     # maroon
        (255, 215, 0),   # gold
        (192, 192, 192), # silver (light grey)
    ],

    # Tints = mix with white at 0/25/50/75/100%
    "red_tints": [
        (255, 0, 0), (255, 64, 64), (255, 128, 128), (255, 191, 191), (255, 255, 255)
    ],
    "green_tints": [
        (0, 255, 0), (64, 255, 64), (128, 255, 128), (191, 255, 191), (255, 255, 255)
    ],
    "blue_tints": [
        (0, 0, 255), (64, 64, 255), (128, 128, 255), (191, 191, 255), (255, 255, 255)
    ],

    # Shades = mix with black at 0/25/50/75/100%
    "red_shades": [
        (255, 0, 0), (191, 0, 0), (128, 0, 0), (64, 0, 0), (0, 0, 0)
    ],
    "green_shades": [
        (0, 255, 0), (0, 191, 0), (0, 128, 0), (0, 64, 0), (0, 0, 0)
    ],
    "blue_shades": [
        (0, 0, 255), (0, 0, 191), (0, 0, 128), (0, 0, 64), (0, 0, 0)
    ],

    "skin_pale": [
        (255, 235, 220),
    ],
    "skin_caucasian": [
        (229, 194, 165),
    ],
    "skin_brown": [
        (170, 120, 90),
    ],
    "skin_dark": [
        (96, 70, 60),
    ],
}

SHADED_PALETTE_SET = extract_rgb_set(SHADED_PALETTE)

NATIVE_WITH_SKIN_PALETTE = {
    "native": [
        (0, 0, 0),       # black
        (255, 255, 255), # white
        (255, 255, 0),   # yellow
        (255, 0, 0),     # red
        (0, 255, 0),     # green
        (0, 0, 255),     # blue
    ],
    "grayscale": [
        (128, 128, 128),
    ],
    "skin_pale": [
        (255, 235, 220),
    ],
    "skin_caucasian": [
        (229, 194, 165),
    ],
    "skin_brown": [
        (170, 120, 90),
    ],
    "skin_dark": [
        (96, 70, 60),
    ],
}

NATIVE_WITH_SKIN_PALETTE_SET = extract_rgb_set(NATIVE_WITH_SKIN_PALETTE)
