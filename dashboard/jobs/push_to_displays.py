from dashboard.constants import (
    JobKind,
)
from dashboard.jobs.image_processing_declaration import RenderDecision, KEEP_PHOTO, ALL_ART_STYLES, ArtStyle
from pathlib import Path
from dashboard.jobs.job_registry import register
from dashboard.models.job import Job
from dashboard.models.photos import SourceImage, Variant
from dashboard.services.logger_job import RunLogger
from pydantic import BaseModel
from dashboard.services.generate_art import run_art_generation_pipeline, ImageProcessingContext
from dashboard.services.classify_image import ImageClassification
from random import random, choice
from typing import cast, Optional
from dashboard.services.scoring import calculate_static_score
from django.utils import timezone

@register('PUSH')
def push_to_displays(job: Job, logger: RunLogger, params: None):
    now = timezone.now()
    base_minute = now.replace(second=0, microsecond=0)
    weekday = "?"
    # 