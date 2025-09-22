from pathlib import Path
from dashboard.constants import RenderDecision
from dashboard.color_constants import PaletteEnum
from dashboard.jobs.job_registry import job_function
from dashboard.services.app_settings import settings
from dashboard.models.job import Job
from dashboard.models.photos import SourceImage, Variant
from dashboard.models.art import (
    Artstyle,
    ArtStyleType,
    ContentType,
)
from dashboard.services.logger_job import JobLogger
from dashboard.services.openai_prompting import (
    get_classification_model,
    GenericImageClassification,
)
from dashboard.services.select_art_style import choose_art_style
from dashboard.image_processing_pipeline import (
    load_pipeline,
    process,
    ImageProcessingPipelineStep,
)
from pydantic import BaseModel
from dataclasses import asdict
from random import random, choices
from typing import cast, List, Tuple
from dashboard.services.scoring import select_random_sources, weighted_geometric_mean
from dashboard.server_types import PrefixedLogger


def decide_art_style(
    source: SourceImage,
    logger: JobLogger,
    no_ai=False,
) -> Tuple[ArtStyleType,str | None]:
    if not source.classification:
        raise Exception("decide_art_style requires a source image with classification")
    if source.classification["renderDecision"] == RenderDecision.LEAVE_PHOTO:
        return ("KEEP_PHOTO", None)
    if source.classification["renderDecision"] == "BOTH" and random() < 0.2:
        return ("KEEP_PHOTO", None)

    # From this point renderDecision is artify
    content_type_record = ContentType.objects.get(
        name=source.classification["contentType"]
    )  # type: ignore
    artstyles = list(
        Artstyle.objects.filter(
            artstylecontenttype__content_type=content_type_record.pk
        )
    )
    if not artstyles:
        raise Exception(
            f"Content type {source.classification['contentType']} not supported yet"
        )  # type: ignore
    if no_ai:
        random_art_style = choices(
            artstyles, weights=[a.score for a in artstyles], k=1
        )[0]
        return (random_art_style.name, None)
    intelligent_choices = choose_art_style(source, logger=logger)
    art_style_list = list(Artstyle.objects.filter(
        name__in=[style.name for style in intelligent_choices.styles] # type: ignore
    ))

    logger.debug(
        f"Art style decision:\n{intelligent_choices.model_dump_json(indent=4)}"
    )
    # AI preference score: first gets 100%, second 80%, third 60%
    # Final weight of the decision 40% to user score, 60% to ai preference (TODO make tuning parameter)
    weights = [
        weighted_geometric_mean([a.score, 1 - (0.2 * float(i))], [0.4, 0.6])
        for i, a in enumerate(art_style_list)
    ]
    random_art_style_choice = choices(intelligent_choices.styles, weights=weights, k=1)[0] # type: ignore
    return (random_art_style_choice.name, random_art_style_choice.context)


PHOTO_PIPELINE: List[ImageProcessingPipelineStep] = [
    ImageProcessingPipelineStep("resize_crop", resolution=(1200, 1600), rotate=90),
    ImageProcessingPipelineStep("p_mode_eink_optimize"),
]


class GenerateVariantParams(BaseModel):
    art_style_override: str | None = None
    max_amount: int = 10


@job_function("generate_variants", GenerateVariantParams)
def generate_variants(
    job: Job,
    logger: JobLogger,
    art_style_override: str | None,
    max_amount: int = 10,
):
    qs = SourceImage.objects.all()
    selection = select_random_sources(list(qs), max_amount)
    for i, src in enumerate(selection):
        classification = GenericImageClassification.from_dict(
            get_classification_model().model_validate(src.classification).model_dump()
        )

        logger.debug(f"Deciding art style for source image")

        art_style_name, art_style_context = (
            (art_style_override, None)
            if art_style_override
            else decide_art_style(src, logger=logger)
        )

        logger.debug(
            f"Starting generation of variant of source image with id {src.pk} with art style {art_style_name}. Context is\n{art_style_context if art_style_context else 'No context given'}"
        )

        photorealist = True
        if classification.art or classification.cartoony:
            photorealist = False
        if art_style_name != "KEEP_PHOTO":
            photorealist = False

        newVariant = Variant.objects.create(
            source_image=src,
            art_style=art_style_name,
            source_quality=classification.quality,
            content_type=classification.contentType,
            photorealist=photorealist,
            generation_context=art_style_context,
        )
        input = Path(src.path)
        output_path = (
            Path(settings().image_generation_dir).resolve()
            / "variants"
            / f"variants_{newVariant.pk}.png"
        )
        if art_style_name == "KEEP_PHOTO":
            pipeline = PHOTO_PIPELINE
        else:
            art_style_record = Artstyle.objects.get(name=art_style_name)
            pre_pipeline = load_pipeline(art_style_record.pre_pipeline)  # type: ignore
            post_pipeline = load_pipeline(art_style_record.post_pipeline)  # type: ignore

            pipeline = (
                pre_pipeline
                + [ImageProcessingPipelineStep("openai_filter", art_style=art_style_name, generation_context=art_style_context)]
                + post_pipeline
                + [ImageProcessingPipelineStep("p_mode_eink_optimize")]
            )

        prefixLogger = PrefixedLogger(
            f"Generating variant nr {i} in {art_style_name} for source image id {src.pk}:",
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
        newVariant.art_style = art_style_name
        newVariant.generation_context = art_style_context
        newVariant.save()
