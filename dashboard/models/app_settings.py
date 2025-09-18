from django.db import models
from solo.models import SingletonModel

class AppSettings(SingletonModel):
    setup_completed= models.BooleanField(
        default=False,
        help_text="True if user completed the wizard"
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

    image_source_dir = models.CharField(
        max_length=255,
        default="~/Pictures",
        help_text="Folder where to find source images to classify and regenerated"
    )

    image_generation_dir = models.CharField(
        max_length=255,
        default="~/Pictures/generated",
        help_text="Folder where to output generated images."
    )

    def __str__(self):
        return "Application Settings"
