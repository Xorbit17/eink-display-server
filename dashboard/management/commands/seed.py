from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from dashboard.models.job import Job 
from dashboard.models.weather import Location
from dashboard.models.calendar import CalendarSource
from dashboard.models.art import Artstyle, ContentType
from dashboard.constants import JobType, JobKind
from dashboard.constants import LOCAL_TZ, ICAL_GOOGLE_CALENDAR_URL

from pathlib import Path


class Command(BaseCommand):
    help = "Seed initial data: periodic jobs, etc."

    @transaction.atomic
    def handle(self, *args, **options):
        """
        Creates or updates a minimal set of cron-based jobs.
        Runs safely multiple times (idempotent).
        """
        seed_jobs = [
            {
                "name": "classify-new-images",
                "kind": JobKind.CLASSIFY,   
                "job_type": JobType.CRON,
                "cron": "*/5 * * * *",  # every 5 minutes
                "enabled": True,
                "params": {},           # add API keys or tuning knobs later if needed
            },
            {
                "name": "generate-art-variants",
                "kind": JobKind.ART,
                "job_type": JobType.CRON,
                "cron": "0 0 * * *",    # every day at midnight
                "enabled": True,
                "params": {},
            },
            {
                "name": "get_weather",
                "kind": JobKind.WEATHER,
                "job_type": JobType.CRON,
                "cron": "55 5 * * *",    # every day at 05:45. Dashboard weather needs to be ready at 06:00
                "enabled": True,
                "params": {},
            },
            {
                "name": "dummy-heartbeat",
                "kind": JobKind.DUMMY,
                "job_type": JobType.CRON,
                "cron": "* * * * *",    # every minute
                "enabled": True,
                "params": {},
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

        seed_calendar_sources = [
            {
                "name": "Default calendar",
                "ics_url": ICAL_GOOGLE_CALENDAR_URL,
                "timezone": LOCAL_TZ,
            }
        ]

        subject_types_prompts_path = Path(__file__).resolve().parent.parent / "context-templates" / "content-type"

        seed_content_types = [
            {
                "name": "Person",
                "classifier_prompt": "",
                "generator_prompt": (subject_types_prompts_path / "person.md").read_text()
            },
            {
                "name": "People",
                "classifier_prompt": "",
                "generator_prompt": (subject_types_prompts_path / "people.md").read_text()
            },
            {
                "name": "Animal",
                "classifier_prompt": "",
                "generator_prompt": (subject_types_prompts_path / "animal.md").read_text()
            },
            {
                "name": "Landscape",
                "classifier_prompt": "",
                "generator_prompt": (subject_types_prompts_path / "landscape.md").read_text()
            },
            {
                "name": "City",
                "classifier_prompt": "",
                "generator_prompt": (subject_types_prompts_path / "city.md").read_text()
            },
            {
                "name": "Building",
                "classifier_prompt": "",
                "generator_prompt": (subject_types_prompts_path / "building.md").read_text()
            },
            {
                "name": "Nature",
                "classifier_prompt": "",
                "generator_prompt": (subject_types_prompts_path / "nature.md").read_text()
            },
            {
                "name": "Art",
                "classifier_prompt": "",
                "generator_prompt": (subject_types_prompts_path / "art.md").read_text()
            },
            {
                "name": "Object",
                "classifier_prompt": "",
                "generator_prompt": (subject_types_prompts_path / "object.md").read_text()
            },
            {
                "name": "Other",
                "classifier_prompt": "",
                "generator_prompt": (subject_types_prompts_path / "other.md").read_text()
            },
        ]

        artstyle_prompt_path = Path(__file__).resolve().parent.parent / "context-templates" / "artstyle"

        seed_art_styles = [
            {
                "name": "keep-photo",
                "description": "Keep the original photograph without applying any transformation.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "keep-photo.md"),
            },
            # Portrait / People friendly classics
            {
                "name": "communist-poster",
                "description": "Art style reminiscent of propaganda posters from Russian or Asian communism.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "communist-poster.md"),
            },
            {
                "name": "studio-ghibli-style",
                "description": "Painterly, soft, and emotional style inspired by Studio Ghibli animations.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "studio-ghibli-style.md"),
            },
            {
                "name": "retro-pixel-art",
                "description": "Low-resolution pixel art style evocative of classic video games.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "retro-pixel-art.md"),
            },
            {
                "name": "pointillism-halftone",
                "description": "Art style using dots or halftone patterns to create shading and form.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "pointillism-halftone.md"),
            },
            {
                "name": "marker-drawing",
                "description": "Hand-drawn look using markers, with visible strokes and bold colors.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "marker-drawing.md"),
            },
            {
                "name": "cubism-abstract-face",
                "description": "Cubist-inspired abstraction with fractured geometric facial features.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "cubism-abstract-face.md"),
            },
            {
                "name": "warhol-pop-art",
                "description": "Bold, repetitive, colorful imagery in the style of Andy Warhol pop art.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "warhol-pop-art.md"),
            },
            {
                "name": "woodcut-linocut",
                "description": "High-contrast relief print look, inspired by traditional woodcut or linocut art.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "woodcut-linocut.md"),
            },
            {
                "name": "minimal-vector-portrait",
                "description": "Flat, minimal portraits created with clean vector shapes and bold blocks of color.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "minimal-vector-portrait.md"),
            },
            {
                "name": "childrens-book-illustration",
                "description": "Whimsical and playful style reminiscent of children’s book illustrations.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "childrens-book-illustration.md"),
            },

            # Modern / Media crossovers
            {
                "name": "pixar-style",
                "description": "3D animated look inspired by Pixar movies, with warm and polished rendering.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "pixar-style.md"),
            },
            {
                "name": "disney-classic",
                "description": "Classic Disney animation style with hand-drawn elegance and timeless appeal.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "disney-classic.md"),
            },
            {
                "name": "spiderverse-comic",
                "description": "Dynamic comic-book inspired style referencing Spider-Verse animation.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "spiderverse-comic.md"),
            },
            {
                "name": "gritty-western-comics",
                "description": "Dark and textured comic book style inspired by gritty Western themes.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "gritty-western-comics.md"),
            },
            {
                "name": "moebius-french-sci-fi",
                "description": "Surreal, intricate linework and coloring inspired by Moebius’ French sci-fi art.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "moebius-french-sci-fi.md"),
            },

            # Group / Scene styles
            {
                "name": "comic-book-vignette",
                "description": "Comic book vignette style with bold lines and dramatic paneling.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "comic-book-vignette.md"),
            },
            {
                "name": "manga-dynamic",
                "description": "Fast-paced, expressive manga style emphasizing motion and action.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "manga-dynamic.md"),
            },
            {
                "name": "ghibli-group-scene",
                "description": "Studio Ghibli inspired large group or ensemble compositions.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "ghibli-group-scene.md"),
            },
            {
                "name": "impressionist-brushwork",
                "description": "Painterly impressionist style with loose, colorful brushwork.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "impressionist-brushwork.md"),
            },
            {
                "name": "silhouette-color-blocks",
                "description": "Simplified silhouettes against bold, flat color backgrounds.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "silhouette-color-blocks.md"),
            },
            {
                "name": "stencil-banksy-style",
                "description": "Stencil-based urban graffiti art inspired by Banksy.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "stencil-banksy-style.md"),
            },

            # Animal-centric
            {
                "name": "ink-watercolor",
                "description": "Delicate watercolor washes with ink outlines for detail.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "ink-watercolor.md"),
            },
            {
                "name": "retro-zoo-poster",
                "description": "Vintage-inspired zoo or animal poster design.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "retro-zoo-poster.md"),
            },
            {
                "name": "naturalist-sketch",
                "description": "Scientific-style naturalist sketches of animals or plants.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "naturalist-sketch.md"),
            },
            {
                "name": "cartoon-mascot",
                "description": "Playful and exaggerated cartoon mascot character designs.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "cartoon-mascot.md"),
            },
            {
                "name": "pixel-sprite-animal",
                "description": "Animal representations in retro pixel sprite format.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "pixel-sprite-animal.md"),
            },
            {
                "name": "lowpoly-geometric",
                "description": "Faceted low-poly geometric representation of objects and animals.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "lowpoly-geometric.md"),
            },
            {
                "name": "papercut-layer-art",
                "description": "Multi-layer paper cut-out style with depth and texture.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "papercut-layer-art.md"),
            },
            {
                "name": "totem-mythological",
                "description": "Totemic and mythological inspired animal/creature designs.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "totem-mythological.md"),
            },

            # Landscape / Nature / City / Building
            {
                "name": "ukiyoe-woodblock",
                "description": "Traditional Japanese Ukiyo-e woodblock print style.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "ukiyoe-woodblock.md"),
            },
            {
                "name": "pencil-graphite",
                "description": "Shaded sketches and drawings made with pencil or graphite.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "pencil-graphite.md"),
            },
            {
                "name": "pastel-poster",
                "description": "Soft pastel coloring applied to poster-style compositions.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "pastel-poster.md"),
            },
            {
                "name": "silkscreen-print",
                "description": "Bold layered ink style inspired by silkscreen printing.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "silkscreen-print.md"),
            },
            {
                "name": "geometric-abstraction",
                "description": "Abstract geometric compositions with strong shapes and symmetry.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "geometric-abstraction.md"),
            },
            {
                "name": "art-deco-travel-poster",
                "description": "Vintage travel poster designs inspired by the Art Deco era.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "art-deco-travel-poster.md"),
            },
            {
                "name": "watercolor-wash",
                "description": "Loose watercolor washes with soft color gradients.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "watercolor-wash.md"),
            },
            {
                "name": "charcoal-drawing",
                "description": "High-contrast sketching with charcoal textures.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "charcoal-drawing.md"),
            },
            {
                "name": "noir-comic-scene",
                "description": "Dark, shadowy noir comic book aesthetics.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "noir-comic-scene.md"),
            },
            {
                "name": "cyberpunk-poster",
                "description": "Neon-lit, futuristic cyberpunk style posters.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "cyberpunk-poster.md"),
            },
            {
                "name": "silkscreen-skyline",
                "description": "Stylized skylines rendered with silkscreen print aesthetics.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "silkscreen-skyline.md"),
            },
            {
                "name": "isometric-pixel-city",
                "description": "Isometric pixel art cityscapes reminiscent of retro games.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "isometric-pixel-city.md"),
            },
            {
                "name": "constructivist-poster",
                "description": "Graphic Soviet-style constructivist poster art.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "constructivist-poster.md"),
            },
            {
                "name": "watercolor-cityscape",
                "description": "Painterly watercolor scenes of urban landscapes.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "watercolor-cityscape.md"),
            },
            {
                "name": "vector-flat-illustration",
                "description": "Flat design vector illustrations with bold colors and simple shapes.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "vector-flat-illustration.md"),
            },
            {
                "name": "blueprint-technical",
                "description": "Technical drawing style resembling engineering blueprints.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "blueprint-technical.md"),
            },
            {
                "name": "woodcut-engraving",
                "description": "Detailed engravings reminiscent of traditional woodcut prints.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "woodcut-engraving.md"),
            },
            {
                "name": "art-deco-architectural-poster",
                "description": "Architectural poster designs inspired by Art Deco aesthetics.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "art-deco-architectural-poster.md"),
            },
            {
                "name": "pop-minimalism",
                "description": "Minimalist style with bold pop-art influenced shapes and colors.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "pop-minimalism.md"),
            },
            {
                "name": "surrealist-deconstruction",
                "description": "Dreamlike, surrealist deconstructions of reality.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "surrealist-deconstruction.md"),
            },
            {
                "name": "stained-glass-style",
                "description": "Intricate designs inspired by stained glass art.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "stained-glass-style.md"),
            },
            {
                "name": "lineart-sketch",
                "description": "Clean line art sketches with minimal shading.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "lineart-sketch.md"),
            },

            # Nature-specific extras
            {
                "name": "botanical-plate",
                "description": "Scientific botanical illustrations showcasing plants in detail.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "botanical-plate.md"),
            },
            {
                "name": "ink-wash-painting",
                "description": "East Asian inspired ink wash painting style.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "ink-wash-painting.md"),
            },
            {
                "name": "stencil-leaves",
                "description": "Stencil-based depictions of leaves and foliage.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "stencil-leaves.md"),
            },
            {
                "name": "cutpaper-collage",
                "description": "Collage aesthetic using layered cut paper textures.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "cutpaper-collage.md"),
            },
            {
                "name": "etching-copperplate",
                "description": "Fine line etching style inspired by copperplate printing.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "etching-copperplate.md"),
            },
            {
                "name": "outline-with-color",
                "description": "Clean outlines filled with flat color areas.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "outline-with-color.md"),
            },
            {
                "name": "art-nouveau-floral",
                "description": "Decorative floral designs inspired by Art Nouveau.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "art-nouveau-floral.md"),
            },

            # Art / Object / Other oriented
            {
                "name": "bauhaus-poster",
                "description": "Graphic poster style inspired by the Bauhaus movement.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "bauhaus-poster.md"),
            },
            {
                "name": "suprematism-minimal-shapes",
                "description": "Minimalist geometric abstraction in the style of Suprematism.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "suprematism-minimal-shapes.md"),
            },
            {
                "name": "op-art-high-contrast",
                "description": "Optical art using high-contrast patterns to create illusions.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "op-art-high-contrast.md"),
            },
            {
                "name": "duotone-poster",
                "description": "Bold duotone color schemes used in modern posters.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "duotone-poster.md"),
            },
            {
                "name": "patent-line-drawing",
                "description": "Technical patent illustrations rendered as line drawings.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "patent-line-drawing.md"),
            },
            {
                "name": "vintage-product-poster",
                "description": "Retro product advertising poster design.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "vintage-product-poster.md"),
            },
            {
                "name": "isometric-pixel-object",
                "description": "Objects rendered in retro isometric pixel art style.",
                "pipeline_definition": [],
                "generator_prompt": (artstyle_prompt_path / "isometric-pixel-object.md"),
            },
        ]

        created, updated = 0, 0

        for spec in seed_jobs:
            obj, was_created = Job.objects.update_or_create(
                name=spec["name"],
                defaults={
                    "kind": spec["kind"],
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


        for cal in seed_calendar_sources:
            obj, was_created = CalendarSource.objects.update_or_create(
                ics_url=cal["ics_url"],
                defaults={
                     "name": cal["name"],
                     "timezone": cal["timezone"]
                },
            )
             
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created CalendarSource: {obj.name}"))
            else:
                updated += 1
                self.stdout.write(self.style.WARNING(f"Updated CalendarSource: {obj.name}"))
            
        for content_type in seed_content_types:
            obj, was_created = ContentType.objects.update_or_create(
                name=content_type["name"],
                defaults={
                    "description": content_type["description"],
                    "classifier_prompt": content_type["classifier_prompt"],
                    "generator_prompt": content_type["generator_prompt"]
                },
            )

            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created Artstyle: {obj.name}"))
            else:
                updated += 1
                self.stdout.write(self.style.WARNING(f"Updated Artstyle: {obj.name}"))

        for style in seed_art_styles:
            obj, was_created = Artstyle.objects.update_or_create(
                name=style["name"],
                defaults={
                    "description": style["description"],
                    "pipeline_definition": style["pipeline_definition"],
                    "generator_prompt": style["generator_prompt"]
                },
            )

            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created Artstyle: {obj.name}"))
            else:
                updated += 1
                self.stdout.write(self.style.WARNING(f"Updated Artstyle: {obj.name}"))

        self.stdout.write(
            self.style.SUCCESS(f"Seeding complete. Created {created}, Updated {updated}")
        )

        self.stdout.write(self.style.SUCCESS(f"Seeding complete. Created: {created}, Updated: {updated}"))
