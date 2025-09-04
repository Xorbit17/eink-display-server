from dashboard.jobs.job_registry import register
from dashboard.constants import (
    IMAGE_DIR,
)
from dashboard.color_constants import EXTENDED_PALETTE_SET
from pathlib import Path
from dashboard.jobs.job_registry import register
from dashboard.models.job import Job
from dashboard.models.application import PrerenderedDashboard
from dashboard.services.logger_job import RunLogger
from dashboard.services.generate_art import run_art_generation_pipeline, ImageProcessingContext
from django.utils import timezone
from dashboard.services.render_page import render_png

@register("DASHBOARD")
def generate_dashboard(job: Job, logger: RunLogger, params):
    now = timezone.now()

    newDashboard = PrerenderedDashboard.objects.create(
        path=None, # None means process started byt generation not funished
    )

    logger.info("Generating dashboard")
    out_path = Path(IMAGE_DIR).resolve() / "dashboards" / f"last_dashboard-{now.strftime('%Y%m%d')}.png"
    url = "http://localhost:8000/dashboard" # TODO wire in env vars for dynamic port allocation

    try:
        png_bytes = render_png(url)
    except Exception as e:
        logger.error(f"Dashboard generation failed\n{str(e)}",)
        raise
    
    logger.info("Running post processing")
    try:
        ctx: ImageProcessingContext = ImageProcessingContext(
            logger=logger,
            pipeline=["quantize_to_palette","output_image"],
            pipeline_args=[(EXTENDED_PALETTE_SET,), ("png",)],
        )
        out_path = run_art_generation_pipeline(png_bytes, context=ctx)
    except Exception as e:
        logger.error(f"Pineline after dashboard failed\n{str(e)}")
        raise
    
    newDashboard.path = str(out_path) # Generation successful
    newDashboard.save()


