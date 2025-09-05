from dashboard.jobs.job_registry import register
from dashboard.constants import (
    IMAGE_DIR,
)
from pathlib import Path
from dashboard.models.job import Job
from dashboard.models.application import PrerenderedDashboard
from dashboard.services.logger_job import JobLogger
from django.utils import timezone
from dashboard.services.render_page import render_png
from dashboard.constants import JobKind
from dashboard.image_processing_pipeline.pipeline_registry import (
    ImageProcessingOutputEnum,
    ImageProcessingPipeline,
    ImageProcessingPipelineStep,
    process,
)
from dashboard.color_constants import PaletteEnum

DASHBOARD_PIPELINE: ImageProcessingPipeline = [
    ImageProcessingPipelineStep("quantize", palette=PaletteEnum.NATIVE)
]


@register(JobKind.DASHBOARD)
def generate_dashboard(job: Job, logger: JobLogger, params):
    now = timezone.now()

    newDashboard = PrerenderedDashboard.objects.create(
        path=None,  # None means process started byt generation not finished
    )

    logger.info("Generating dashboard")
    out_path = (
        Path(IMAGE_DIR).resolve()
        / "dashboards"
        / f"last_dashboard-{now.strftime('%Y%m%d')}.png"
    )
    url = "http://localhost:8000/dashboard"  # TODO wire in env vars for dynamic port allocation

    try:
        png_bytes = render_png(url)
    except Exception as e:
        logger.error(
            f"Dashboard generation failed\n{str(e)}",
        )
        raise

    logger.info("Running post processing")
    try:
        out_path = process(
            png_bytes,
            DASHBOARD_PIPELINE,
            output_format=ImageProcessingOutputEnum.FILE,
            output_path=out_path,
            logger=logger,
        )
    except Exception as e:
        logger.error(f"Pineline failed\n{str(e)}")
        raise

    newDashboard.path = str(out_path)  # Generation successful
    newDashboard.save()
