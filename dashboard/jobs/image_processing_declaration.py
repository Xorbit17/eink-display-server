from typing import List, Tuple, Final, Dict, Callable, Any, Literal, TypeAlias
from dashboard.color_constants import SHADED_PALETTE_SET
from dataclasses import dataclass


NOT_SUITED: Final[str] = "NOT_SUITED"
BAD: Final[str] = "BAD"
PASSABLE: Final[str] = "PASSABLE"
GOOD: Final[str] = "GOOD"
VERY_GOOD: Final[str] = "VERY_GOOD"

QualityClassification: TypeAlias = Literal[
    "NOT_SUITED",
    "BAD",
    "PASSABLE",
    "GOOD",
    "VERY_GOOD",
]

QUALITY_CLASSIFICATION_CHOICES = [
    (NOT_SUITED, "Not suited"),
    (BAD, "Bad"),
    (PASSABLE, "Passable"),
    (GOOD, "Good"),
    (VERY_GOOD, "Very good"),
]

PERSON: Final[str] = "PERSON"
PEOPLE: Final[str] = "PEOPLE"
ANIMAL: Final[str] = "ANIMAL"
LANDSCAPE: Final[str] = "LANDSCAPE"
CITY: Final[str] = "CITY"
BUILDING: Final[str] = "BUILDING"
NATURE: Final[str] = "NATURE"
ART: Final[str] = "ART"
OBJECT: Final[str] = "OBJECT"
OTHER: Final[str] = "OTHER"

ContentTypeClassification: TypeAlias = Literal[
    "PERSON",
    "PEOPLE",
    "ANIMAL",
    "LANDSCAPE",
    "CITY",
    "BUILDING",
    "NATURE",
    "ART",
    "OBJECT",
    "OTHER",
]

CONTENT_TYPE_MARKDOWN: Dict[ContentTypeClassification,str] = {
    "PERSON":"person.md",
    "PEOPLE":"people.md",
    "ANIMAL":"animal.md",
    "LANDSCAPE":"landscape.md",
    "CITY":"city.md",
    "BUILDING":"building.md",
    "NATURE":"nature.md",
    "ART":"art.md",
    "OBJECT":"object.md",
    "OTHER":"other.md",
}

CONTENT_TYPE_CLASSIFICATION_CHOICES = [
    (PERSON, "Person"),
    (PEOPLE, "People"),
    (ANIMAL, "Animal"),
    (LANDSCAPE, "Landscape"),
    (CITY, "City"),
    (BUILDING, "Building"),
    (NATURE, "Nature"),
    (ART, "Art"),
    (OBJECT, "Object"),
    (OTHER, "Other"),
]

BOTH: Final[str] = "BOTH"
ARTIFY: Final[str] = "ARTIFY"
LEAVE_PHOTO: Final[str] = "LEAVE_PHOTO"

RenderDecision: TypeAlias = Literal[
    "BOTH",
    "ARTIFY",
    "LEAVE_PHOTO",
]

RENDER_DECISION_CHOICES = [
    (BOTH, "Both"),
    (ARTIFY, "Artify"),
    (LEAVE_PHOTO, "Leave photo"),
]

KEEP_PHOTO="KEEP_PHOTO"
# Portrait / People friendly classics
COMMUNIST_POSTER = "COMMUNIST_POSTER"
STUDIO_GHIBLI_STYLE = "STUDIO_GHIBLI_STYLE"
RETRO_PIXEL_ART = "RETRO_PIXEL_ART"
POINTILLISM_HALFTONE = "POINTILLISM_HALFTONE"
MARKER_DRAWING = "MARKER_DRAWING"  # Needs more specific
CUBISM_ABSTRACT_FACE = "CUBISM_ABSTRACT_FACE"
WARHOL_POP_ART = "WARHOL_POP_ART"
WOODCUT_LINOCUT = "WOODCUT_LINOCUT"
MINIMAL_VECTOR_PORTRAIT = "MINIMAL_VECTOR_PORTRAIT"
CHILDRENS_BOOK_ILLUSTRATION = "CHILDRENS_BOOK_ILLUSTRATION"  # Needs more specific

# Modern/Media crossovers
PIXAR_STYLE = "PIXAR_STYLE"
DISNEY_CLASSIC = "DISNEY_CLASSIC"
SPIDERVERSE_COMIC = "SPIDERVERSE_COMIC"
GRITTY_WESTERN_COMICS = "GRITTY_WESTERN_COMICS"
MOEBIUS_FRENCH_SCI_FI = "MOEBIUS_FRENCH_SCI_FI"  # Needs more specifics, Jean giraud

# Group/scene styles
COMIC_BOOK_VIGNETTE = "COMIC_BOOK_VIGNETTE"
MANGA_DYNAMIC = "MANGA_DYNAMIC"
GHIBLI_GROUP_SCENE = "GHIBLI_GROUP_SCENE"
IMPRESSIONIST_BRUSHWORK = "IMPRESSIONIST_BRUSHWORK"
SILHOUETTE_COLOR_BLOCKS = "SILHOUETTE_COLOR_BLOCKS"
STENCIL_BANKSY_STYLE = "STENCIL_BANKSY_STYLE"

# Animal-centric
INK_WATERCOLOR = "INK_WATERCOLOR"
RETRO_ZOO_POSTER = "RETRO_ZOO_POSTER"
NATURALIST_SKETCH = "NATURALIST_SKETCH"
CARTOON_MASCOT = "CARTOON_MASCOT"
PIXEL_SPRITE_ANIMAL = "PIXEL_SPRITE_ANIMAL"
LOWPOLY_GEOMETRIC = "LOWPOLY_GEOMETRIC"
PAPERCUT_LAYER_ART = "PAPERCUT_LAYER_ART"
TOTEM_MYTHOLOGICAL = "TOTEM_MYTHOLOGICAL"

# Landscape / Nature / City / Building
UKIYOE_WOODBLOCK = "UKIYOE_WOODBLOCK"
PENCIL_GRAPHITE = "PENCIL_GRAPHITE"
PASTEL_POSTER = "PASTEL_POSTER"
SILKSCREEN_PRINT = "SILKSCREEN_PRINT"
GEOMETRIC_ABSTRACTION = "GEOMETRIC_ABSTRACTION"
ART_DECO_TRAVEL_POSTER = "ART_DECO_TRAVEL_POSTER"
WATERCOLOR_WASH = "WATERCOLOR_WASH"
CHARCOAL_DRAWING = "CHARCOAL_DRAWING"

NOIR_COMIC_SCENE = "NOIR_COMIC_SCENE"
CYBERPUNK_POSTER = "CYBERPUNK_POSTER"
SILKSCREEN_SKYLINE = "SILKSCREEN_SKYLINE"
ISOMETRIC_PIXEL_CITY = "ISOMETRIC_PIXEL_CITY"
CONSTRUCTIVIST_POSTER = "CONSTRUCTIVIST_POSTER"
WATERCOLOR_CITYSCAPE = "WATERCOLOR_CITYSCAPE"
VECTOR_FLAT_ILLUSTRATION = "VECTOR_FLAT_ILLUSTRATION"

BLUEPRINT_TECHNICAL = "BLUEPRINT_TECHNICAL"
WOODCUT_ENGRAVING = "WOODCUT_ENGRAVING"
ART_DECO_ARCHITECTURAL_POSTER = "ART_DECO_ARCHITECTURAL_POSTER"
POP_MINIMALISM = "POP_MINIMALISM"
SURREALIST_DECONSTRUCTION = "SURREALIST_DECONSTRUCTION"
STAINED_GLASS_STYLE = "STAINED_GLASS_STYLE"
LINEART_SKETCH = "LINEART_SKETCH"

# Nature-specific extras
BOTANICAL_PLATE = "BOTANICAL_PLATE"
INK_WASH_PAINTING = "INK_WASH_PAINTING"
STENCIL_LEAVES = "STENCIL_LEAVES"
CUTPAPER_COLLAGE = "CUTPAPER_COLLAGE"
ETCHING_COPPERPLATE = "ETCHING_COPPERPLATE"
OUTLINE_WITH_COLOR = "OUTLINE_WITH_COLOR"
ART_NOUVEAU_FLORAL = "ART_NOUVEAU_FLORAL"

# ART / OBJECT / OTHER oriented
BAUHAUS_POSTER = "BAUHAUS_POSTER"
SUPREMATISM_MINIMAL_SHAPES = "SUPREMATISM_MINIMAL_SHAPES"
OP_ART_HIGH_CONTRAST = "OP_ART_HIGH_CONTRAST"
DUOTONE_POSTER = "DUOTONE_POSTER"
PATENT_LINE_DRAWING = "PATENT_LINE_DRAWING"
VINTAGE_PRODUCT_POSTER = "VINTAGE_PRODUCT_POSTER"
ISOMETRIC_PIXEL_OBJECT = "ISOMETRIC_PIXEL_OBJECT"

ArtStyle: TypeAlias = Literal[
    "KEEP_PHOTO",
    # Portrait / People friendly classics
    "COMMUNIST_POSTER",
    "STUDIO_GHIBLI_STYLE",
    "RETRO_PIXEL_ART",
    "POINTILLISM_HALFTONE",
    "MARKER_DRAWING",
    "CUBISM_ABSTRACT_FACE",
    "WARHOL_POP_ART",
    "WOODCUT_LINOCUT",
    "MINIMAL_VECTOR_PORTRAIT",
    "CHILDRENS_BOOK_ILLUSTRATION",

    # Modern/Media crossovers
    "PIXAR_STYLE",
    "DISNEY_CLASSIC",
    "SPIDERVERSE_COMIC",
    "GRITTY_WESTERN_COMICS",
    "MOEBIUS_FRENCH_SCI_FI",

    # Group/scene styles
    "COMIC_BOOK_VIGNETTE",
    "MANGA_DYNAMIC",
    "GHIBLI_GROUP_SCENE",
    "IMPRESSIONIST_BRUSHWORK",
    "SILHOUETTE_COLOR_BLOCKS",
    "STENCIL_BANKSY_STYLE",

    # Animal-centric
    "INK_WATERCOLOR",
    "RETRO_ZOO_POSTER",
    "NATURALIST_SKETCH",
    "CARTOON_MASCOT",
    "PIXEL_SPRITE_ANIMAL",
    "LOWPOLY_GEOMETRIC",
    "PAPERCUT_LAYER_ART",
    "TOTEM_MYTHOLOGICAL",

    # Landscape / Nature / City / Building
    "UKIYOE_WOODBLOCK",
    "PENCIL_GRAPHITE",
    "PASTEL_POSTER",
    "SILKSCREEN_PRINT",
    "GEOMETRIC_ABSTRACTION",
    "ART_DECO_TRAVEL_POSTER",
    "WATERCOLOR_WASH",
    "CHARCOAL_DRAWING",

    "NOIR_COMIC_SCENE",
    "CYBERPUNK_POSTER",
    "SILKSCREEN_SKYLINE",
    "ISOMETRIC_PIXEL_CITY",
    "CONSTRUCTIVIST_POSTER",
    "WATERCOLOR_CITYSCAPE",
    "VECTOR_FLAT_ILLUSTRATION",

    "BLUEPRINT_TECHNICAL",
    "WOODCUT_ENGRAVING",
    "ART_DECO_ARCHITECTURAL_POSTER",
    "POP_MINIMALISM",
    "SURREALIST_DECONSTRUCTION",
    "STAINED_GLASS_STYLE",
    "LINEART_SKETCH",

    # Nature-specific extras
    "BOTANICAL_PLATE",
    "INK_WASH_PAINTING",
    "STENCIL_LEAVES",
    "CUTPAPER_COLLAGE",
    "ETCHING_COPPERPLATE",
    "OUTLINE_WITH_COLOR",
    "ART_NOUVEAU_FLORAL",

    # ART / OBJECT / OTHER oriented
    "BAUHAUS_POSTER",
    "SUPREMATISM_MINIMAL_SHAPES",
    "OP_ART_HIGH_CONTRAST",
    "DUOTONE_POSTER",
    "PATENT_LINE_DRAWING",
    "VINTAGE_PRODUCT_POSTER",
    "ISOMETRIC_PIXEL_OBJECT",
]

ART_STYLE_CHOICES = [
    (KEEP_PHOTO, "Keep the original"),
    # Portrait / People friendly classics
    (COMMUNIST_POSTER, "Communist Poster"),
    (STUDIO_GHIBLI_STYLE, "Studio Ghibli Style"),
    (RETRO_PIXEL_ART, "Retro Pixel Art"),
    (POINTILLISM_HALFTONE, "Pointillism / Halftone"),
    (MARKER_DRAWING, "Marker Drawing"),
    (CUBISM_ABSTRACT_FACE, "Cubism Abstract Face"),
    (WARHOL_POP_ART, "Warhol Pop Art"),
    (WOODCUT_LINOCUT, "Woodcut / Linocut"),
    (MINIMAL_VECTOR_PORTRAIT, "Minimal Vector Portrait"),
    (CHILDRENS_BOOK_ILLUSTRATION, "Children's Book Illustration"),

    # Modern / Media crossovers
    (PIXAR_STYLE, "Pixar Style"),
    (DISNEY_CLASSIC, "Disney Classic"),
    (SPIDERVERSE_COMIC, "Spiderverse Comic"),
    (GRITTY_WESTERN_COMICS, "Gritty Western Comics"),
    (MOEBIUS_FRENCH_SCI_FI, "Moebius (French Sci-Fi)"),

    # Group / Scene styles
    (COMIC_BOOK_VIGNETTE, "Comic Book Vignette"),
    (MANGA_DYNAMIC, "Manga Dynamic"),
    (GHIBLI_GROUP_SCENE, "Ghibli Group Scene"),
    (IMPRESSIONIST_BRUSHWORK, "Impressionist Brushwork"),
    (SILHOUETTE_COLOR_BLOCKS, "Silhouette Color Blocks"),
    (STENCIL_BANKSY_STYLE, "Stencil (Banksy Style)"),

    # Animal-centric
    (INK_WATERCOLOR, "Ink Watercolor"),
    (RETRO_ZOO_POSTER, "Retro Zoo Poster"),
    (NATURALIST_SKETCH, "Naturalist Sketch"),
    (CARTOON_MASCOT, "Cartoon Mascot"),
    (PIXEL_SPRITE_ANIMAL, "Pixel Sprite Animal"),
    (LOWPOLY_GEOMETRIC, "Low-Poly Geometric"),
    (PAPERCUT_LAYER_ART, "Papercut Layer Art"),
    (TOTEM_MYTHOLOGICAL, "Totem / Mythological"),

    # Landscape / Nature / City / Building
    (UKIYOE_WOODBLOCK, "Ukiyo-e Woodblock"),
    (PENCIL_GRAPHITE, "Pencil / Graphite"),
    (PASTEL_POSTER, "Pastel Poster"),
    (SILKSCREEN_PRINT, "Silkscreen Print"),
    (GEOMETRIC_ABSTRACTION, "Geometric Abstraction"),
    (ART_DECO_TRAVEL_POSTER, "Art Deco Travel Poster"),
    (WATERCOLOR_WASH, "Watercolor Wash"),
    (CHARCOAL_DRAWING, "Charcoal Drawing"),

    (NOIR_COMIC_SCENE, "Noir Comic Scene"),
    (CYBERPUNK_POSTER, "Cyberpunk Poster"),
    (SILKSCREEN_SKYLINE, "Silkscreen Skyline"),
    (ISOMETRIC_PIXEL_CITY, "Isometric Pixel City"),
    (CONSTRUCTIVIST_POSTER, "Constructivist Poster"),
    (WATERCOLOR_CITYSCAPE, "Watercolor Cityscape"),
    (VECTOR_FLAT_ILLUSTRATION, "Vector Flat Illustration"),

    (BLUEPRINT_TECHNICAL, "Blueprint / Technical"),
    (WOODCUT_ENGRAVING, "Woodcut Engraving"),
    (ART_DECO_ARCHITECTURAL_POSTER, "Art Deco Architectural Poster"),
    (POP_MINIMALISM, "Pop Minimalism"),
    (SURREALIST_DECONSTRUCTION, "Surrealist Deconstruction"),
    (STAINED_GLASS_STYLE, "Stained Glass Style"),
    (LINEART_SKETCH, "Lineart Sketch"),

    # Nature-specific extras
    (BOTANICAL_PLATE, "Botanical Plate"),
    (INK_WASH_PAINTING, "Ink Wash Painting"),
    (STENCIL_LEAVES, "Stencil Leaves"),
    (CUTPAPER_COLLAGE, "Cut-Paper Collage"),
    (ETCHING_COPPERPLATE, "Etching / Copperplate"),
    (OUTLINE_WITH_COLOR, "Outline with Color"),
    (ART_NOUVEAU_FLORAL, "Art Nouveau Floral"),

    # Art / Object / Other oriented
    (BAUHAUS_POSTER, "Bauhaus Poster"),
    (SUPREMATISM_MINIMAL_SHAPES, "Suprematism (Minimal Shapes)"),
    (OP_ART_HIGH_CONTRAST, "Op-Art High Contrast"),
    (DUOTONE_POSTER, "Duotone Poster"),
    (PATENT_LINE_DRAWING, "Patent Line Drawing"),
    (VINTAGE_PRODUCT_POSTER, "Vintage Product Poster"),
    (ISOMETRIC_PIXEL_OBJECT, "Isometric Pixel Object"),
]

PipelineStyle: TypeAlias = ArtStyle | Literal["KEEP_PHOTO"]
PipelineSteps: TypeAlias = list[str]
PipelineArgs: TypeAlias  = list[Tuple]

PipelineDeclaration: TypeAlias = tuple[PipelineStyle, PipelineSteps, PipelineArgs]

DEFAULT_KEEP_PHOTO: PipelineDeclaration = (
    "KEEP_PHOTO",
    ["resize_crop", "output_image"],
    [(None,),("png",)],
)

PERSON_ART_STYLES: List[PipelineDeclaration] = [
    DEFAULT_KEEP_PHOTO,
    (
        COMMUNIST_POSTER,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("communist-poster.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        STUDIO_GHIBLI_STYLE,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("studio-ghibli-style.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        PIXAR_STYLE,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("pixar-style.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        DISNEY_CLASSIC,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("disney-classic.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        SPIDERVERSE_COMIC,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("spiderverse-comic.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        RETRO_PIXEL_ART,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("retro-pixel-art.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        POINTILLISM_HALFTONE,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("pointillism-halftone.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        MARKER_DRAWING,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("marker-drawing.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        CUBISM_ABSTRACT_FACE,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("cubism-abstract-face.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        WARHOL_POP_ART,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("warhol-pop-art.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        WOODCUT_LINOCUT,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("woodcut-linocut.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        MINIMAL_VECTOR_PORTRAIT,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("minimal-vector-portrait.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        CHILDRENS_BOOK_ILLUSTRATION,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("childrens-book-illustration.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        MOEBIUS_FRENCH_SCI_FI,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("moebius-french-sci-fi.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
]

PEOPLE_ART_STYLES: List[PipelineDeclaration] = [
    DEFAULT_KEEP_PHOTO,
    (
        COMIC_BOOK_VIGNETTE,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("comic-book-vignette.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        MANGA_DYNAMIC,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("manga-dynamic.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        GHIBLI_GROUP_SCENE,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("ghibli-group-scene.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        SPIDERVERSE_COMIC,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("spiderverse-comic.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        GRITTY_WESTERN_COMICS,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("gritty-western-comics.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        STENCIL_BANKSY_STYLE,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("stencil-banksy-style.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        CHILDRENS_BOOK_ILLUSTRATION,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("childrens-book-illustration.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        STUDIO_GHIBLI_STYLE,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("studio-ghibli-style.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        PIXAR_STYLE,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("pixar-style.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        DISNEY_CLASSIC,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("disney-classic.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        MOEBIUS_FRENCH_SCI_FI,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("moebius-french-sci-fi.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
]

ANIMAL_ART_STYLES: List[PipelineDeclaration] = [
    DEFAULT_KEEP_PHOTO,
    (
        INK_WATERCOLOR,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("ink-watercolor.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        RETRO_ZOO_POSTER,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("retro-zoo-poster.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        NATURALIST_SKETCH,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("naturalist-sketch.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        CARTOON_MASCOT,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("cartoon-mascot.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        PIXEL_SPRITE_ANIMAL,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("pixel-sprite-animal.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        LOWPOLY_GEOMETRIC,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("lowpoly-geometric.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        PAPERCUT_LAYER_ART,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("papercut-layer-art.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        TOTEM_MYTHOLOGICAL,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("totem-mythisch-totem.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        WOODCUT_ENGRAVING,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("woodcut-engraving.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        STUDIO_GHIBLI_STYLE,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("studio-ghibli-style.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        DISNEY_CLASSIC,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("disney-classic.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        PIXAR_STYLE,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("pixar-style.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
]

LANDSCAPE_ART_STYLES: List[PipelineDeclaration] = [
    DEFAULT_KEEP_PHOTO,
    (
        UKIYOE_WOODBLOCK,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("ukiyoe-woodblock.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        PENCIL_GRAPHITE,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("pencil-graphite.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        PASTEL_POSTER,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("pastel-poster.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        SILKSCREEN_PRINT,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("silkscreen-print.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        GEOMETRIC_ABSTRACTION,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("geometric-abstraction.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        ART_DECO_TRAVEL_POSTER,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("art-deco-travel-poster.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        WATERCOLOR_WASH,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("watercolor-wash.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        CHARCOAL_DRAWING,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("charcoal-drawing.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        MOEBIUS_FRENCH_SCI_FI,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("moebius-french-sci-fi.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
]

NATURE_ART_STYLES: List[PipelineDeclaration] = [
    DEFAULT_KEEP_PHOTO,
    (
        BOTANICAL_PLATE,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("botanical-plate.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        INK_WASH_PAINTING,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("ink-wash-painting.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        STENCIL_LEAVES,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("stencil-leaves.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        CUTPAPER_COLLAGE,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("cutpaper-collage.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        ETCHING_COPPERPLATE,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("etching-copperplate.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        OUTLINE_WITH_COLOR,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("outline-with-color.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        ART_NOUVEAU_FLORAL,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("art-nouveau-floral.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        UKIYOE_WOODBLOCK,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("ukiyoe-woodblock.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        WATERCOLOR_WASH,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("watercolor-wash.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        POINTILLISM_HALFTONE,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("pointillism-halftone.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        SILHOUETTE_COLOR_BLOCKS,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("silhouette-color-blocks.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
]

CITY_ART_STYLES: List[PipelineDeclaration] = [
    DEFAULT_KEEP_PHOTO,
    (
        NOIR_COMIC_SCENE,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("noir-comic-scene.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        CYBERPUNK_POSTER,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("cyberpunk-poster.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        SILKSCREEN_SKYLINE,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("silkscreen-skyline.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        ISOMETRIC_PIXEL_CITY,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("isometric-pixel-city.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        CONSTRUCTIVIST_POSTER,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("constructivist-poster.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        WATERCOLOR_CITYSCAPE,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("watercolor-cityscape.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        VECTOR_FLAT_ILLUSTRATION,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("vector-flat-illustration.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        ART_DECO_ARCHITECTURAL_POSTER,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("art-deco-architectural-poster.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        UKIYOE_WOODBLOCK,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("ukiyoe-woodblock.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        SPIDERVERSE_COMIC,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("spiderverse-comic.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        GRITTY_WESTERN_COMICS,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("gritty-western-comics.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        MOEBIUS_FRENCH_SCI_FI,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("moebius-french-sci-fi.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        BLUEPRINT_TECHNICAL,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("blueprint-technical.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        SILHOUETTE_COLOR_BLOCKS,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("silhouette-color-blocks.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
]

BUILDING_ART_STYLES: List[PipelineDeclaration] = [
    DEFAULT_KEEP_PHOTO,
    (
        BLUEPRINT_TECHNICAL,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("blueprint-technical.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        WOODCUT_ENGRAVING,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("woodcut-engraving.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        ART_DECO_ARCHITECTURAL_POSTER,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("art-deco-architectural-poster.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        POP_MINIMALISM,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("pop-minimalism.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        SURREALIST_DECONSTRUCTION,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("surrealist-deconstruction.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        STAINED_GLASS_STYLE,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("stained-glass-style.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
    (
        LINEART_SKETCH,
        ["openai_process", "resize_crop", "quantize_to_palette", "output_image"],
        [("lineart-sketch.md",), (None,), (SHADED_PALETTE_SET,), ("png",)],
    ),
]

ALL_ART_STYLES: Dict[ContentTypeClassification, List[PipelineDeclaration] | None] = {
    "PERSON": PERSON_ART_STYLES,
    "PEOPLE": PEOPLE_ART_STYLES,
    "ANIMAL": ANIMAL_ART_STYLES,
    "LANDSCAPE": LANDSCAPE_ART_STYLES,
    "CITY": CITY_ART_STYLES,
    "BUILDING": BUILDING_ART_STYLES,
    "NATURE": NATURE_ART_STYLES,
    "ART": None,
    "OBJECT": None,
    "OTHER": None,
}
