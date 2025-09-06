from __future__ import annotations
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from dashboard.models.app_settings import AppSettings
from dashboard.models.job import Job 
from dashboard.models.weather import Location
from dashboard.models.calendar import CalendarSource
from dashboard.models.art import Artstyle, ContentType, ArtstyleContentType
from dashboard.constants import JobType

from pathlib import Path

TIME_ZONE = getattr(settings, "TIME_ZONE", 'Europe/Brussels')


class Command(BaseCommand):
    help = "Seed initial data: periodic jobs, etc."

    @transaction.atomic
    def handle(self, *args, **options):
        appSettings = AppSettings.get_solo()
        appSettings.source_image_dir = os.environ.get("IMAGE_INPUT_DIR","/app/input")
        appSettings.generate_image_dir = os.environ.get("GENERATED_OUTPUT_DIR",'/app/generate')
        appSettings.discovery_port = int(os.environ.get("DISCOVERY_PORT","51234"))
        appSettings.openai_key=os.environ.get("OPENAI_API_KEY", None)
        appSettings.openweathermap_key=os.environ.get("OPENWEATHERMAP_API_KEY", None)
        appSettings.save()

        seed_jobs = [
            {
                "name": "classify-new-images",
                "job_function_name": "classify",   
                "job_type": JobType.CRON,
                "cron": "*/5 * * * *",  # every 5 minutes
                "enabled": False,
                "params": {},
                "order": 100, # In case other jobs are executed this one goes last
            },
            {
                "name": "generate-art-variants",
                "job_function_name": "generate_variants",
                "job_type": JobType.CRON,
                "cron": "0 0 * * *",    # every day at midnight
                "enabled": False,
                "params": {}, # TODO
                "order": 0,
            },
            {
                "name": "get_weather",
                "job_function_name": "get_weather",
                "job_type": JobType.CRON,
                "cron": "55 5 * * *",    # weather and calendar need to be ready at 06:00
                "enabled": False,
                "params": {},
                "order": 0,
            },
            {
                "name": "get_calendar",
                "job_function_name": "get_calendar",
                "job_type": JobType.CRON,
                "cron": "55 5 * * *",    # weather and calendar need to be ready at 06:00
                "enabled": False,
                "params": {},
                "order": 1,
            },
            {
                "name": "generate_dashboard",
                "job_function_name": "generate_dashboard",
                "job_type": JobType.CRON,
                "cron": "59 * * * *",    # One minute before the hour. Dashboard needs to be ready at hour change
                "enabled": False,
                "params": {},
            },
            {
                "name": "dummy",
                "job_function_name": "dummy",
                "job_type": JobType.CRON,
                "cron": "* * * * *",    # every minute
                "enabled": False,
                "params": {
                    "message":"Daemon heartbeat"
                },
                "order":101
            },
        ]

        seed_locations= [
            {
                "name": "Blankenberge",
                "country": "BE",
                "latitude": "51°18'15.5\"N",
                "longitude": "3°08'44.0\"E",
            }
        ]

        subject_types_prompts_path = Path(__file__).resolve().parent.parent.parent / "context-templates" / "content-type"

        seed_content_types = [
            {
                "name": "Person",
                "classifier_prompt": "",
                "generator_prompt": (subject_types_prompts_path / "person.md").read_text(),
                "score":"0.5",
            },
            {
                "name": "People",
                "classifier_prompt": "",
                "generator_prompt": (subject_types_prompts_path / "people.md").read_text(),
                "score":"0.5",
            },
            {
                "name": "Animal",
                "classifier_prompt": "",
                "generator_prompt": (subject_types_prompts_path / "animal.md").read_text(),
                "score":"0.5",
            },
            {
                "name": "Landscape",
                "classifier_prompt": "",
                "generator_prompt": (subject_types_prompts_path / "landscape.md").read_text(),
                "score":"0.5",
            },
            {
                "name": "City",
                "classifier_prompt": "",
                "generator_prompt": (subject_types_prompts_path / "city.md").read_text(),
                "score":"0.5",
            },
            {
                "name": "Building",
                "classifier_prompt": "",
                "generator_prompt": (subject_types_prompts_path / "building.md").read_text(),
                "score":"0.5",
            },
            {
                "name": "Nature",
                "classifier_prompt": "",
                "generator_prompt": (subject_types_prompts_path / "nature.md").read_text(),
                "score":"0.5",
            },
            {
                "name": "Art",
                "classifier_prompt": "",
                "generator_prompt": (subject_types_prompts_path / "art.md").read_text(),
                "score":"0.5",
            },
            {
                "name": "Object",
                "classifier_prompt": "",
                "generator_prompt": (subject_types_prompts_path / "object.md").read_text(),
                "score":"0.5",
            },
            {
                "name": "Other",
                "classifier_prompt": "",
                "generator_prompt": (subject_types_prompts_path / "other.md").read_text(),
                "score":"0.5",
            },
        ]

        all_content_type_names = set([content_type.get("name") for content_type in seed_content_types])


        artstyle_prompt_path = Path(__file__).resolve().parent.parent / "context-templates" / "artstyle"

        seed_art_styles = [
            {
                "name": "keep-photo",
                "description": "Keep the original photograph without applying any transformation.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "keep-photo.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            # Portrait / People friendly classics
            {
                "name": "communist-poster",
                "description": "Art style reminiscent of propaganda posters from Russian or Asian communism.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "communist-poster.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "studio-ghibli-style",
                "description": "Painterly, soft, and emotional style inspired by Studio Ghibli animations.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "studio-ghibli-style.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "retro-pixel-art",
                "description": "Low-resolution pixel art style evocative of classic video games.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "retro-pixel-art.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "pointillism-halftone",
                "description": "Art style using dots or halftone patterns to create shading and form.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "pointillism-halftone.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "marker-drawing",
                "description": "Hand-drawn look using markers, with visible strokes and bold colors.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "marker-drawing.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "cubism-abstract-face",
                "description": "Cubist-inspired abstraction with fractured geometric facial features.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "cubism-abstract-face.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "warhol-pop-art",
                "description": "Bold, repetitive, colorful imagery in the style of Andy Warhol pop art.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "warhol-pop-art.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "woodcut-linocut",
                "description": "High-contrast relief print look, inspired by traditional woodcut or linocut art.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "woodcut-linocut.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "minimal-vector-portrait",
                "description": "Flat, minimal portraits created with clean vector shapes and bold blocks of color.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "minimal-vector-portrait.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "childrens-book-illustration",
                "description": "Whimsical and playful style reminiscent of children’s book illustrations.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "childrens-book-illustration.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },

            # Modern / Media crossovers
            {
                "name": "pixar-style",
                "description": "3D animated look inspired by Pixar movies, with warm and polished rendering.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "pixar-style.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "disney-classic",
                "description": "Classic Disney animation style with hand-drawn elegance and timeless appeal.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "disney-classic.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "spiderverse-comic",
                "description": "Dynamic comic-book inspired style referencing Spider-Verse animation.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "spiderverse-comic.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "gritty-western-comics",
                "description": "Dark and textured comic book style inspired by gritty Western themes.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "gritty-western-comics.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "moebius-french-sci-fi",
                "description": "Surreal, intricate linework and coloring inspired by Moebius’ French sci-fi art.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "moebius-french-sci-fi.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },

            # Group / Scene styles
            {
                "name": "comic-book-vignette",
                "description": "Comic book vignette style with bold lines and dramatic paneling.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "comic-book-vignette.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "manga-dynamic",
                "description": "Fast-paced, expressive manga style emphasizing motion and action.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "manga-dynamic.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "ghibli-group-scene",
                "description": "Studio Ghibli inspired large group or ensemble compositions.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "ghibli-group-scene.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "impressionist-brushwork",
                "description": "Painterly impressionist style with loose, colorful brushwork.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "impressionist-brushwork.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "silhouette-color-blocks",
                "description": "Simplified silhouettes against bold, flat color backgrounds.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "silhouette-color-blocks.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "stencil-banksy-style",
                "description": "Stencil-based urban graffiti art inspired by Banksy.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "stencil-banksy-style.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },

            # Animal-centric
            {
                "name": "ink-watercolor",
                "description": "Delicate watercolor washes with ink outlines for detail.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "ink-watercolor.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "retro-zoo-poster",
                "description": "Vintage-inspired zoo or animal poster design.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "retro-zoo-poster.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "naturalist-sketch",
                "description": "Scientific-style naturalist sketches of animals or plants.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "naturalist-sketch.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "cartoon-mascot",
                "description": "Playful and exaggerated cartoon mascot character designs.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "cartoon-mascot.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "pixel-sprite-animal",
                "description": "Animal representations in retro pixel sprite format.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "pixel-sprite-animal.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "lowpoly-geometric",
                "description": "Faceted low-poly geometric representation of objects and animals.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "lowpoly-geometric.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "papercut-layer-art",
                "description": "Multi-layer paper cut-out style with depth and texture.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "papercut-layer-art.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "totem-mythological",
                "description": "Totemic and mythological inspired animal/creature designs.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "totem-mythological.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },

            # Landscape / Nature / City / Building
            {
                "name": "ukiyoe-woodblock",
                "description": "Traditional Japanese Ukiyo-e woodblock print style.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "ukiyoe-woodblock.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "pencil-graphite",
                "description": "Shaded sketches and drawings made with pencil or graphite.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "pencil-graphite.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "pastel-poster",
                "description": "Soft pastel coloring applied to poster-style compositions.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "pastel-poster.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "silkscreen-print",
                "description": "Bold layered ink style inspired by silkscreen printing.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "silkscreen-print.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "geometric-abstraction",
                "description": "Abstract geometric compositions with strong shapes and symmetry.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "geometric-abstraction.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "art-deco-travel-poster",
                "description": "Vintage travel poster designs inspired by the Art Deco era.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "art-deco-travel-poster.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "watercolor-wash",
                "description": "Loose watercolor washes with soft color gradients.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "watercolor-wash.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "charcoal-drawing",
                "description": "High-contrast sketching with charcoal textures.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "charcoal-drawing.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "noir-comic-scene",
                "description": "Dark, shadowy noir comic book aesthetics.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "noir-comic-scene.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "cyberpunk-poster",
                "description": "Neon-lit, futuristic cyberpunk style posters.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "cyberpunk-poster.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "silkscreen-skyline",
                "description": "Stylized skylines rendered with silkscreen print aesthetics.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "silkscreen-skyline.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "isometric-pixel-city",
                "description": "Isometric pixel art cityscapes reminiscent of retro games.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "isometric-pixel-city.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "constructivist-poster",
                "description": "Graphic Soviet-style constructivist poster art.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "constructivist-poster.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "watercolor-cityscape",
                "description": "Painterly watercolor scenes of urban landscapes.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "watercolor-cityscape.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "vector-flat-illustration",
                "description": "Flat design vector illustrations with bold colors and simple shapes.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "vector-flat-illustration.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "blueprint-technical",
                "description": "Technical drawing style resembling engineering blueprints.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "blueprint-technical.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "woodcut-engraving",
                "description": "Detailed engravings reminiscent of traditional woodcut prints.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "woodcut-engraving.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "art-deco-architectural-poster",
                "description": "Architectural poster designs inspired by Art Deco aesthetics.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "art-deco-architectural-poster.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "pop-minimalism",
                "description": "Minimalist style with bold pop-art influenced shapes and colors.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "pop-minimalism.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "surrealist-deconstruction",
                "description": "Dreamlike, surrealist deconstructions of reality.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "surrealist-deconstruction.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "stained-glass-style",
                "description": "Intricate designs inspired by stained glass art.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "stained-glass-style.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "lineart-sketch",
                "description": "Clean line art sketches with minimal shading.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "lineart-sketch.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },

            # Nature-specific extras
            {
                "name": "botanical-plate",
                "description": "Scientific botanical illustrations showcasing plants in detail.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "botanical-plate.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "ink-wash-painting",
                "description": "East Asian inspired ink wash painting style.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "ink-wash-painting.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "stencil-leaves",
                "description": "Stencil-based depictions of leaves and foliage.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "stencil-leaves.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "cutpaper-collage",
                "description": "Collage aesthetic using layered cut paper textures.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "cutpaper-collage.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,            },
            {
                "name": "etching-copperplate",
                "description": "Fine line etching style inspired by copperplate printing.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "etching-copperplate.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "outline-with-color",
                "description": "Clean outlines filled with flat color areas.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "outline-with-color.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "art-nouveau-floral",
                "description": "Decorative floral designs inspired by Art Nouveau.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "art-nouveau-floral.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },

            # Art / Object / Other oriented
            {
                "name": "bauhaus-poster",
                "description": "Graphic poster style inspired by the Bauhaus movement.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "bauhaus-poster.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "suprematism-minimal-shapes",
                "description": "Minimalist geometric abstraction in the style of Suprematism.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "suprematism-minimal-shapes.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "op-art-high-contrast",
                "description": "Optical art using high-contrast patterns to create illusions.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "op-art-high-contrast.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "duotone-poster",
                "description": "Bold duotone color schemes used in modern posters.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "duotone-poster.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "patent-line-drawing",
                "description": "Technical patent illustrations rendered as line drawings.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "patent-line-drawing.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "vintage-product-poster",
                "description": "Retro product advertising poster design.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "vintage-product-poster.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "isometric-pixel-object",
                "description": "Objects rendered in retro isometric pixel art style.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "isometric-pixel-object.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
        ]

        created, updated = 0, 0

        for spec in seed_jobs:
            obj, was_created = Job.objects.update_or_create(
                name=spec["name"],
                defaults={
                    "job_function_name": spec["job_function_name"],
                    "job_type": spec["job_type"],
                    "cron": spec["cron"],
                    "enabled": spec["enabled"],
                    "params": spec["params"],
                },
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created job: {obj.name}"))
            else:
                updated += 1
                self.stdout.write(self.style.WARNING(f"Updated job: {obj.name}"))

        for spec in seed_locations:
            obj, was_created = Location.objects.update_or_create(
                name=spec["name"],
                country=spec["country"],
                defaults={
                    "latitude": spec["latitude"],
                    "longitude": spec["longitude"]
                },

            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created Location: {obj.name}"))
            else:
                updated += 1
                self.stdout.write(self.style.WARNING(f"Updated Location: {obj.name}"))

        content_type_cache = {}
        for content_type in seed_content_types:
            obj, was_created = ContentType.objects.update_or_create(
                name=content_type["name"],
                defaults={
                    "description": content_type["description"],
                    "classifier_prompt": content_type["classifier_prompt"],
                    "generator_prompt": content_type["generator_prompt"]
                },
            )
            content_type_cache[content_type["name"]] = obj
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created Artstyle: {obj.name}"))
            else:
                updated += 1
                self.stdout.write(self.style.WARNING(f"Updated Artstyle: {obj.name}"))


        for style in seed_art_styles:
            artstyle, was_created = Artstyle.objects.update_or_create(
                name=style["name"],
                defaults={
                    "description": style["description"],
                    "pipeline_definition": style["pipeline_definition"],
                    "generator_prompt": style["generator_prompt"]
                },
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created Artstyle: {artstyle.name}"))
            else:
                updated += 1
                self.stdout.write(self.style.WARNING(f"Updated Artstyle: {artstyle.name}"))

            for name in style["allowed_content_types"]:
                content_type = content_type_cache[name]
                obj = ArtstyleContentType.objects.create(
                    artstyle=artstyle,
                    content_type=content_type
                )

                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created ArtstyleContentType: {artstyle.name}-{content_type.name}"))



        self.stdout.write(
            self.style.SUCCESS(f"Seeding complete. Created {created}, Updated {updated}")
        )

        self.stdout.write(self.style.SUCCESS(f"Seeding complete. Created: {created}, Updated: {updated}"))
