from pathlib import Path
from dashboard.constants import RenderDecision
from dashboard.jobs.job_registry import job_function
from dashboard.services.app_settings import settings
from dashboard.models.job import Job
from dashboard.models.photos import SourceImage, Variant
from dashboard.models.art import (
    Artstyle,
    ArtStyleType,
)
from dashboard.services.logger_job import JobLogger
from dashboard.services.openai_prompting import (
    get_classification_model,
    GenericImageClassification,
)
from dashboard.image_processing_pipeline import (
    load_pipeline,
    process,
    ImageProcessingPipeline,
    ImageProcessingPipelineStep,
)
from pydantic import BaseModel
from random import random, choices
from typing import cast
from dashboard.services.scoring import select_random_sources
from dashboard.server_types import PrefixedLogger

def decide_art_style(classification: GenericImageClassification) -> ArtStyleType:
    if classification.renderDecision == RenderDecision.LEAVE_PHOTO:
        return "KEEP_PHOTO"
    if classification.renderDecision == "BOTH" and random() < 0.2:
        return "KEEP_PHOTO"

    # From this point renderDecision is artify
    artstyles = list(
        Artstyle.objects.filter(
            artstylecontenttype__content_type=classification.contentType
        )
    )
    if not artstyles:
        raise Exception(f"Content type {classification.contentType} not supported yet")

    random_art_style = choices(artstyles, weights=[a.score for a in artstyles], k=1)[0]
    return random_art_style.name


class GenerateVariantParams(BaseModel):
    art_style_override: str | None = None
    max_amount: int = 10


PHOTO_PIPELINE: ImageProcessingPipeline = [
    ImageProcessingPipelineStep("resize_crop", resolution=(1200, 1600))
]

@job_function("generate_variants", GenerateVariantParams)
def generate_variants(
    job: Job,
    logger: JobLogger,
    art_style_override: str | None,
    max_amount: int,
):
    qs = SourceImage.objects.all()
    selection = select_random_sources(list(qs), max_amount)
    for i, src in enumerate(selection):
        classification = cast(
            GenericImageClassification,
            get_classification_model().model_validate(src.classification),
        )

        art_style = art_style_override if art_style_override else decide_art_style(classification)

        logger.debug(
            f"Starting generation of variant of source image with id {src.pk} with art style {art_style}"
        )

        photorealist = True
        if classification.art or classification.cartoony:
            photorealist = False
        if art_style != "KEEP_PHOTO":
            photorealist = False

        newVariant = Variant.objects.create(
            source_image=src,
            art_style=art_style,
            source_quality=classification.quality,
            ContentType=classification.contentType,
            photorealist=photorealist,
        )
        input = Path(src.path)
        output_path = Path(settings().generate_image_dir).resolve() / "variants" / f"variants_{src.pk}.png"
        if art_style == "KEEP_PHOTO":
            pipeline = PHOTO_PIPELINE
        else:
            art_style_record = Artstyle.objects.get(name=art_style)
            pipeline = load_pipeline(art_style_record.pipeline_definition)
        prefixLogger = PrefixedLogger(
            f"Generating variant nr {i} in {art_style} for source image id {src.pk}:",
            logger,
        )
        process(
            input,
            pipeline,
            output_path=output_path,
            classification=classification,
            logger=prefixLogger,
        )
        prefixLogger.info("Pipeline finished.")
        newVariant.path = str(output_path)
        newVariant.art_style = art_style
        newVariant.save()
