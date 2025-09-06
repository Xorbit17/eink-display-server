from django.db import models
from solo.models import SingletonModel

class AppSettings(SingletonModel):
    setup_completed= models.BooleanField(
        default=False,
        help_text="True if user completed the wizard"
    )
    source_image_dir = models.CharField(
        max_length=512,
        help_text="Base directory where source images are stored.",
        default="/app/input"
    )
    generate_image_dir = models.CharField(
        max_length=512,
        help_text="Directory for generated artifacts.",
        default="/app/generate"
    )

    discovery_port = models.PositiveIntegerField(
        default=51234,
        help_text="UDP port for device discovery."
    )

    openai_key = models.CharField(
        max_length=255,
        null=True,
        help_text="OpenAI API key.",
        default=None,
    )
    openweathermap_key = models.CharField(
        max_length=255,
        null=True,
        help_text="OpenWeatherMap API key.",
        default=None,
    )
    image_art_generation_model = models.CharField(
        max_length=128,
        default="gpt-5",
        help_text="Model for art generation."
    )
    image_classification_model = models.CharField(
        max_length=128,
        default="gpt-5",
        help_text="Model for image classification."
    )

    def __str__(self):
        return "Application Settings"
