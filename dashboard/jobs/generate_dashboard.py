from dashboard.jobs.job_registry import job_function
from pathlib import Path
from dashboard.services.app_settings import settings
from dashboard.models.job import Job
from dashboard.models.application import PrerenderedDashboard
from dashboard.services.logger_job import JobLogger
from django.utils import timezone
from dashboard.services.render_page import render_png
from dashboard.image_processing_pipeline import (
    ImageProcessingPipeline,
    ImageProcessingPipelineStep,
    process,
)
from dashboard.color_constants import PaletteEnum

DASHBOARD_PIPELINE: ImageProcessingPipeline = [
    ImageProcessingPipelineStep("quantize", palette=PaletteEnum.NATIVE)
]

@job_function("generate_dashboard")
def generate_dashboard(job: Job, logger: JobLogger, **kwargs):
    now = timezone.now()

    newDashboard = PrerenderedDashboard.objects.create(
        path=None,  # None means process started byt generation not finished
    )

    logger.info("Generating dashboard")
    out_path = (
        Path(settings().image_generation_dir).resolve()
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
    out_path = process(
        png_bytes,
        DASHBOARD_PIPELINE,
        output_path=out_path,
        logger=logger,
    )

    newDashboard.path = str(out_path)  # Generation successful
    newDashboard.save()
