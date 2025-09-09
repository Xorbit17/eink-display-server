from __future__ import annotations
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from dashboard.color_constants import PaletteEnum
from dashboard.models.app_settings import AppSettings
from dashboard.models.job import Job 
from dashboard.models.weather import Location
from dashboard.models.calendar import CalendarSource
from dashboard.models.art import Artstyle, ContentType, ArtstyleContentType
from dashboard.constants import JobType
from dashboard.image_processing_pipeline import ImageProcessingPipelineStep, dump_pipeline

from pathlib import Path

TIME_ZONE = getattr(settings, "TIME_ZONE", 'Europe/Brussels')

def read_file(path: Path, default="", throw=True) -> str:
    try:
        return Path(path).read_text()
    except os.error as e:
        if throw:
            raise e
        else:
            return default


class Command(BaseCommand):
    help = "Seed initial data: periodic jobs, etc."

    @transaction.atomic
    def handle(self, *args, **options):
        appSettings = AppSettings.get_solo()
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
                "params": {
                    "max_num_to_classify": 10,
                },
                "order": 100, # In case other jobs are executed this one goes last
            },
            {
                "name": "generate-art-variants",
                "job_function_name": "generate_variants",
                "job_type": JobType.CRON,
                "cron": "0 0 * * *",    # every day at midnight
                "enabled": False,
                "params": {
                    "max_amount": 3,
                },
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
                "name": "Portrait",
                "classifier_prompt": "Image showing a sharp, clear portrait of a person.",
                "generator_prompt": (subject_types_prompts_path / "portrait.md"),
                "score":0.5,
            },
            {
                "name": "Person",
                "classifier_prompt": "Image showing a single person (full body, not portrait)",
                "generator_prompt": (subject_types_prompts_path / "person.md"),
                "score":0.5,
            },
            {
                "name": "People",
                "classifier_prompt": "Image showing multiple People clearly in frame. Also applicable when one or more People's bodies are outside of the frame.",
                "generator_prompt": (subject_types_prompts_path / "people.md"),
                "score":0.5,
            },
            {
                "name": "Animal",
                "classifier_prompt": "Image showing a clear picture of an animal or a plant -- especially pets -- in which the larger part of the image is taken up by the animal/plant or a part of the animal/plant.",
                "generator_prompt": (subject_types_prompts_path / "animal.md"),
                "score":0.5,
            },
            {
                "name": "Landscape",
                "classifier_prompt": "Image showing a landscape from afar. Such as mountains, a forest, a beach, a view from high up a tower, ...",
                "generator_prompt": (subject_types_prompts_path / "landscape.md"),
                "score":0.5,
            },
            {
                "name": "City",
                "classifier_prompt": "Image showing a city scape; not with the focus on an individual building or on People.",
                "generator_prompt": (subject_types_prompts_path / "city.md"),
                "score":0.5,
            },
            {
                "name": "Building",
                "classifier_prompt": "Image showing a single building prominently of which a large part of the image is taken up by the building or part of the building.",
                "generator_prompt": (subject_types_prompts_path / "building.md"),
                "score":0.5,
            },
            {
                "name": "Nature",
                "classifier_prompt": "Images showing waterfalls, plats, trees, corals, groves, ... Subject needs to be natural but the zoom level cannot be too far. Far zoomed out images are considered landscapes; not 'nature' images.",
                "generator_prompt": (subject_types_prompts_path / "nature.md"),
                "score":0.5,
            },
            {
                "name": "Art",
                "classifier_prompt": "An image showing an artwork such as a statue, painting, drawing, music score, book cover, woodcutting, sewing work, clothing design or something else. The artwork needs to take up by far the largest part of the image.",
                "generator_prompt": (subject_types_prompts_path / "art.md"),
                "score":0.5,
            },
            {
                "name": "Object",
                "classifier_prompt": "An image showing an object which is not necessarily art but is interesting. The object needs to take up a large part of the image, needs to be in the foreground and in focus. Examples are cars, motorbikes, bicycles, tanks, airplans, electronic devices, coffee makers, tools, personal accessories, ...",
                "generator_prompt": (subject_types_prompts_path / "object.md"),
                "score":0.5,
            },
            {
                "name": "Other",
                "classifier_prompt": "Fallback catchall content type.",
                "generator_prompt": (subject_types_prompts_path / "other.md"),
                "score":0.5,
            },
        ]

        all_content_type_names = set([content_type.get("name") for content_type in seed_content_types])
        
        def no_quant_pipeline():
            return dump_pipeline([
                ImageProcessingPipelineStep("resize_crop", resolution=(1200,1600))
            ])
        def quant_pipeline(palette: PaletteEnum):
            return dump_pipeline([
                ImageProcessingPipelineStep("resize_crop", resolution=(1200,1600)),
                ImageProcessingPipelineStep("quantize", palette=palette)
            ])

        artstyle_prompt_path = Path(__file__).resolve().parent.parent.parent / "context-templates" / "art_style"

        seed_art_styles = [
            {
                "name": "communist-poster",
                "description": "Art style reminiscent of propaganda posters from Russian or Asian communism.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.EXTENDED),
                "generator_prompt": (artstyle_prompt_path / "communist-poster.md"),
                "allowed_content_types": ["Person","People","Portrait"],
                "score":0.5,
            },
            {
                "name": "studio-ghibli-style",
                "description": "Painterly, soft, and emotional style inspired by Studio Ghibli animation film stills. Painterly backgrounds, expressive characters and dramatic cinematic lighting.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.SHADED),
                "generator_prompt": (artstyle_prompt_path / "studio-ghibli-style.md"),
                "allowed_content_types": ["Person","People","Portrait"],
                "score":0.5,
            },
            {
                "name": "retro-pixel-art",
                "description": "Low-resolution pixel art style evocative of classic video games.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.SHADED),
                "generator_prompt": (artstyle_prompt_path / "retro-pixel-art.md"),
                "allowed_content_types": ["Portrait","Object"],
                "score":0.5,
            },
            {
                "name": "pointillism-halftone",
                "description": "Art style using dots or halftone patterns to create shading and form.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.NATIVE),
                "generator_prompt": (artstyle_prompt_path / "pointillism-halftone.md"),
                "allowed_content_types": ["Nature","Landscape","Person","Portrait"],
                "score":0.5,
            },
            {
                "name": "marker-drawing",
                "description": "Hand-drawn look using markers, with visible strokes and bold colors.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.EXTENDED_NATIVE_SKIN),
                "generator_prompt": (artstyle_prompt_path / "marker-drawing.md"),
                "allowed_content_types": ["Person","People","Portrait", "Object", "Building", "Animal"],
                "score":0.5,
            },
            {
                "name": "cubism-abstract-face",
                "description": "Cubist-inspired abstraction with fractured geometric facial features.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.EXTENDED_NATIVE_SKIN),
                "generator_prompt": (artstyle_prompt_path / "cubism-abstract-face.md"),
                "allowed_content_types": ["Portrait"],
                "score":0.5,
            },
            {
                "name": "warhol-pop-art",
                "description": "Bold, repetitive, colorful imagery in the style of Andy Warhol pop art.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.EXTENDED_NATIVE_SKIN),
                "generator_prompt": (artstyle_prompt_path / "warhol-pop-art.md"),
                "allowed_content_types": ["Person","People","Portrait"],
                "score":0.5,
            },
            {
                "name": "woodcut-linocut",
                "description": "High-contrast relief print look, inspired by traditional woodcut or linocut art.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.WOODCUT),
                "generator_prompt": (artstyle_prompt_path / "woodcut-linocut.md"),
                "allowed_content_types": ["Portrait","Object","Person","Animal","Nature"],
                "score":0.5,
            },
            {
                "name": "minimal-vector-portrait",
                "description": "Flat, minimal portraits created with clean vector shapes and bold blocks of color.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.EXTENDED_NATIVE_SKIN),
                "generator_prompt": (artstyle_prompt_path / "minimal-vector-portrait.md"),
                "allowed_content_types": ["Portrait","Animal","Object"],
                "score":0.5,
            },
            {
                "name": "childrens-book-illustration",
                "description": "Whimsical and playful style reminiscent of children's book illustrations.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.EXTENDED_NATIVE_SKIN),
                "generator_prompt": (artstyle_prompt_path / "childrens-book-illustration.md"),
                "allowed_content_types": ["Person","People","Portrait","City"],
                "score":0.5,
            },
            {
                "name": "pixar-style",
                "description": "3D animated look inspired by Pixar movies, with warm and polished rendering.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.SHADED),
                "generator_prompt": (artstyle_prompt_path / "pixar-style.md"),
                "allowed_content_types": ["Person","People","Portrait","Animal"],
                "score":0.5,
            },
            {
                "name": "disney-classic",
                "description": "Classic Disney animation style with hand-drawn elegance and timeless appeal.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.SHADED),
                "generator_prompt": (artstyle_prompt_path / "disney-classic.md"),
                "allowed_content_types": ["Person","People","Portrait","Animal"],
                "score":0.5,
            },
            {
                "name": "spiderverse-comic",
                "description": "Dynamic comic-book inspired style referencing Spider-Verse animation.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.SHADED),
                "generator_prompt": (artstyle_prompt_path / "spiderverse-comic.md"),
                "allowed_content_types": ["Person","People","Portrait","City","Building"],
                "score":0.5,
            },
            {
                "name": "gritty-western-comics",
                "description": "Dark and textured comic book style inspired by gritty Western themes.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.SHADED),
                "generator_prompt": (artstyle_prompt_path / "gritty-western-comics.md"),
                "allowed_content_types": ["Person","People","Portrait","Nature"],
                "score":0.5,
            },
            {
                "name": "moebius-french-sci-fi",
                "description": "Surreal, intricate linework and coloring inspired by Moebius' French sci-fi art.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.SHADED),
                "generator_prompt": (artstyle_prompt_path / "moebius-french-sci-fi.md"),
                "allowed_content_types": ["City","Building","People"],
                "score":0.5,
            },
            {
                "name": "manga-dynamic",
                "description": "Fast-paced, expressive manga style emphasizing motion and action.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.SHADED),
                "generator_prompt": (artstyle_prompt_path / "manga-dynamic.md"),
                "allowed_content_types": ["Person","People","Portrait"],
                "score":0.5,
            },
            {
                "name": "ink-watercolor",
                "description": "Delicate watercolor washes with ink outlines for detail.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.SHADED),
                "generator_prompt": (artstyle_prompt_path / "ink-watercolor.md"),
                "allowed_content_types": ["Person","Portrait", "Object","Nature","Animal"],
                "score":0.5,
            },
            {
                "name": "retro-zoo-poster",
                "description": "Vintage-inspired zoo or animal poster design.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.SHADED),
                "generator_prompt": (artstyle_prompt_path / "retro-zoo-poster.md"),
                "allowed_content_types": ["Animal"],
                "score":0.5,
            },
            {
                "name": "naturalist-sketch",
                "description": "Scientific-style naturalist sketches of animals or plants.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.EXTENDED),
                "generator_prompt": (artstyle_prompt_path / "naturalist-sketch.md"),
                "allowed_content_types": ["Animal"],
                "score":0.5,
            },
            {
                "name": "cartoon-mascot",
                "description": "Playful and exaggerated cartoon mascot character designs.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.EXTENDED_NATIVE_SKIN),
                "generator_prompt": (artstyle_prompt_path / "cartoon-mascot.md"),
                "allowed_content_types": ["Portrait", "Person", "Animal"],
                "score":0.5,
            },
            {
                "name": "lowpoly-geometric",
                "description": "Faceted low-poly geometric representation of objects and animals.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.EXTENDED_NATIVE_SKIN),
                "generator_prompt": (artstyle_prompt_path / "lowpoly-geometric.md"),
                "allowed_content_types": ["Person","Animal","Object"],
                "score":0.5,
            },
            {
                "name": "papercut-layer-art",
                "description": "Multi-layer paper cut-out style with depth and texture.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.EXTENDED_NATIVE_SKIN),
                "generator_prompt": (artstyle_prompt_path / "papercut-layer-art.md"),
                "allowed_content_types": ["Nature","People","Person","Animal"],
                "score":0.5,
            },
            {
                "name": "totem-mythological",
                "description": "Totemic and mythological inspired animal/creature designs.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.SHADED),
                "generator_prompt": (artstyle_prompt_path / "totem-mythological.md"),
                "allowed_content_types": ["People", "Portrait"],
                "score":0.5,
            },

            # Landscape / Nature / City / Building
            {
                "name": "impressionist-brushwork",
                "description": "Painterly impressionist style with loose, colorful brushwork.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.SHADED),
                "generator_prompt": (artstyle_prompt_path / "impressionist-brushwork.md"),
                "allowed_content_types": ["City","Building","Nature","Landscape"],
                "score":0.5,
            },
            {
                "name": "ukiyoe-woodblock",
                "description": "Traditional Japanese Ukiyo-e woodblock print style.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.WOOD_EXTENDED),
                "generator_prompt": (artstyle_prompt_path / "ukiyoe-woodblock.md"),
                "allowed_content_types": ["People","Person","City"],
                "score":0.5,
            },
            {
                "name": "pencil-graphite",
                "description": "Shaded sketches and drawings made with pencil or graphite.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.GRAYSCALE),
                "generator_prompt": (artstyle_prompt_path / "pencil-graphite.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "silkscreen-print",
                "description": "Bold layered ink style inspired by silkscreen printing.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.EXTENDED_NATIVE_SKIN),
                "generator_prompt": (artstyle_prompt_path / "silkscreen-print.md"),
                "allowed_content_types": ["Object", "Portrait","Person","Animal"],
                "score":0.5,
            },
            {
                "name": "art-deco-travel-poster",
                "description": "Vintage travel poster designs inspired by the Art Deco era.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.SHADED),
                "generator_prompt": (artstyle_prompt_path / "art-deco-travel-poster.md"),
                "allowed_content_types": ["Landscape","City"],
                "score":0.5,
            },
            {
                "name": "cyberpunk-poster",
                "description": "Neon-lit, futuristic cyberpunk style posters.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.SHADED),
                "generator_prompt": (artstyle_prompt_path / "cyberpunk-poster.md"),
                "allowed_content_types": ["People","City","Building","Person"],
                "score":0.5,
            },
            {
                "name": "constructivist-poster",
                "description": "Graphic Soviet-style constructivist poster art.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.EXTENDED),
                "generator_prompt": (artstyle_prompt_path / "constructivist-poster.md"),
                "allowed_content_types": ["City","Building"],
                "score":0.5,
            },
            {
                "name": "blueprint-technical",
                "description": "Technical drawing style resembling engineering blueprints.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.EXTENDED),
                "generator_prompt": (artstyle_prompt_path / "blueprint-technical.md"),
                "allowed_content_types": ["Object"],
                "score":0.5,
            },
            {
                "name": "woodcut-engraving",
                "description": "Detailed engravings reminiscent of traditional woodcut prints.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.WOODCUT),
                "generator_prompt": (artstyle_prompt_path / "woodcut-engraving.md"),
                "allowed_content_types": ["Portrait","Animal","Object","Building"],
                "score":0.5,
            },
            {
                "name": "art-deco-architectural-poster",
                "description": "Architectural poster designs inspired by Art Deco aesthetics.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.SHADED),
                "generator_prompt": (artstyle_prompt_path / "art-deco-architectural-poster.md"),
                "allowed_content_types": ["Building", "City"],
                "score":0.5,
            },
            {
                "name": "pop-minimalism",
                "description": "Minimalist style with bold pop-art influenced shapes and colors.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.NATIVE),
                "generator_prompt": (artstyle_prompt_path / "pop-minimalism.md"),
                "allowed_content_types": ["Portrait","Person","Object"],
                "score":0.5,
            },
            {
                "name": "stained-glass-style",
                "description": "Intricate designs inspired by stained glass art.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.SHADED),
                "generator_prompt": (artstyle_prompt_path / "stained-glass-style.md"),
                "allowed_content_types": ["Portrait","Person"],
                "score":0.5,
            },
            {
                "name": "digital-lineart-sketch",
                "description": "Clean line art sketches with minimal shading that looks as if it was created with a digital touch stylus and screen in photoshop.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.GRAYSCALE),
                "generator_prompt": (artstyle_prompt_path / "digital-lineart-sketch.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },

            # Nature-specific extras
            {
                "name": "ink-wash-painting",
                "description": "East Asian inspired ink wash painting style.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.SHADED),
                "generator_prompt": (artstyle_prompt_path / "ink-wash-painting.md"),
                "allowed_content_types": all_content_type_names,
                "score":0.5,
            },
            {
                "name": "etching-copperplate",
                "description": "Fine line etching style inspired by copperplate printing.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.GRAYSCALE),
                "generator_prompt": (artstyle_prompt_path / "etching-copperplate.md"),
                "allowed_content_types": ["Person","Object","Building"],
                "score":0.5,
            },
            # Art / Object / Other oriented
            {
                "name": "bauhaus-poster",
                "description": "Graphic poster style inspired by the Bauhaus movement.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.SHADED),
                "generator_prompt": (artstyle_prompt_path / "bauhaus-poster.md"),
                "allowed_content_types": ["Building"],
                "score":0.5,
            },
            {
                "name": "vintage-product-poster",
                "description": "Retro product advertising poster design.",
                "pre_pipeline": [],
                "post_pipeline": quant_pipeline(PaletteEnum.NATIVE),
                "generator_prompt": (artstyle_prompt_path / "vintage-product-poster.md"),
                "allowed_content_types": ["Object"],
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
                    "classifier_prompt": content_type["classifier_prompt"],
                    "generator_prompt": read_file(content_type["generator_prompt"]),
                },
            )
            content_type_cache[obj.name] = obj
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created Artstyle: {obj.name}"))
            else:
                updated += 1
                self.stdout.write(self.style.WARNING(f"Updated Artstyle: {obj.name}"))


        for style in seed_art_styles:
            art_style, was_created = Artstyle.objects.update_or_create(
                name=style["name"],
                defaults={
                    "description": style["description"],
                    "pre_pipeline": style["pre_pipeline"],
                    "post_pipeline": style["post_pipeline"],
                    "generator_prompt": read_file(style["generator_prompt"])
                },
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created Artstyle: {art_style.name}"))
            else:
                updated += 1
                self.stdout.write(self.style.WARNING(f"Updated Artstyle: {art_style.name}"))

            for name in style["allowed_content_types"]:
                content_type = content_type_cache[name]
                obj = ArtstyleContentType.objects.create(
                    art_style=art_style,
                    content_type=content_type
                )

                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created ArtstyleContentType: {art_style.name}-{content_type.name}"))



        self.stdout.write(
            self.style.SUCCESS(f"Seeding complete. Created {created}, Updated {updated}")
        )

        self.stdout.write(self.style.SUCCESS(f"Seeding complete. Created: {created}, Updated: {updated}"))
