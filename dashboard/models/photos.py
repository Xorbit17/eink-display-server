from django.db import models
from dashboard.constants import QualityClassification
class SourceImage(models.Model):
    path = models.TextField()
    classification = models.JSONField(null=True, default=None)  # null => not classified yet
    score = models.FloatField(default=0.5)
    favorite = models.BooleanField(default = False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def has_variants(self) -> bool:
        return self.variants.exists() # type: ignore

    def __str__(self) -> str:
        return f"SourceImage({self.pk}): {self.path}"
    
class Variant(models.Model):
    source_image = models.ForeignKey(
        "SourceImage",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="variants",
    )
    path = models.TextField(null=True, default=None) # Null means variant was created but generation has crashed
    art_style = models.CharField(max_length=64)

    score=models.FloatField(default=0.5)
    
    source_quality = models.CharField(choices=QualityClassification.choices())
    content_type = models.CharField(max_length=64)
    photorealist = models.BooleanField()
    favorite = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self) -> str:
        return f"Variant({self.pk}): {self.path} (art_style:{self.art_style})"

