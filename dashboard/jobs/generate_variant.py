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

class GenerateVariantParams(BaseModel):
    source_image_id: int
    art_style_force: Optional[ArtStyle]

def decide_art_style(classification: ImageClassification) ->  ArtStyle:
    if (classification.renderDecision == "LEAVE_PHOTO"):
        return KEEP_PHOTO
    decision: RenderDecision = "ARTIFY"
    if (classification.renderDecision == "BOTH"):
        decision= "LEAVE_PHOTO" if random() < 0.2 else "ARTIFY"
    if decision == "LEAVE_PHOTO":
        return KEEP_PHOTO
    
    # Select a random art style that is not KEEP PHOTO
    art_styles = ALL_ART_STYLES.get(classification.contentType)
    if not art_styles:
        raise Exception(f"Content type {classification.contentType} not supported yet")
    art_style_list = [t[0] for t in art_styles][1:]
    random_art_style = choice(art_style_list)
    return cast(ArtStyle,random_art_style)

@register('ART', GenerateVariantParams)
def generate_variant(job: Job, logger: RunLogger, params: GenerateVariantParams | None):
    if not params:
        raise RuntimeError("generate variant requires params")
    src = SourceImage.objects.get(pk=params.source_image_id)
    if not src:
        raise RuntimeError(f"Source image with id {params.source_image_id} not found")

    if not src.classification:
        raise RuntimeError("Image has not been calassified yet. Cannot create variant")
    classification = ImageClassification.model_validate(src.classification)
    logger.debug(f"Starting generation of variant of source image with id {src.pk}")

    input = Path(src.path)
    art_style = decide_art_style(classification)
    art_styles = ALL_ART_STYLES.get(classification.contentType)
    
    if not art_styles:
        raise RuntimeError('Impossible')
    
    photorealist = True
    if (classification.art or classification.cartoony):
        photorealist = False
    if (art_style != KEEP_PHOTO):
        photorealist = False
        
    newVariant = Variant.objects.create(
        source_image=src,
        score=calculate_static_score(
            classification.quality,
            classification.contentType,
            photorealist
        )
    )

    pipeline_info = next(t for t in art_styles if t[0]==art_style)
    context = ImageProcessingContext(
        classification=classification,
        art_style=art_style,
        pipeline=pipeline_info[1],
        pipeline_args=pipeline_info[2],
        logger=logger,
    )
    ext = pipeline_info[2][-1]
    output = input.resolve().parent / "variants" / f"variants_{src.pk}.{ext}"
    try:
        run_art_generation_pipeline(
            input,
            output,
            context=context
        )
        logger.info("Image processing pipeline finished for artwork.")
        newVariant.path = str(output)
        newVariant.art_style = art_style
        newVariant.save()
        logger._close_success("Image processing pipeline finished")
    except BaseException as e:
        logger._close_error(e)

    
