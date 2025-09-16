from __future__ import annotations

import os
import random
from pathlib import Path
from dashboard.services.app_settings import settings
from dashboard.models.job import Job
from dashboard.models.photos import SourceImage
from dashboard.services.logger_job import JobLogger
from dashboard.services.scoring import calculate_static_score_for_source
from dashboard.constants import (
    IMAGE_EXTENSIONS,
    IMAGE_INPUT_DIR,
    GENERATED_OUTPUT_DIR,
)
from dashboard.services.classify_image import classify_image
from dashboard.jobs.job_registry import job_function
from PIL import Image
from pydantic import BaseModel
from typing import Optional
import json

def find_files() -> set[str]:
    """Return absolute paths of images in settings.source_image_dir (no subdirs)."""
    try:
        entries = os.listdir(IMAGE_INPUT_DIR)
    except FileNotFoundError:
        raise RuntimeError(f"Image source directory does not exist \"{IMAGE_INPUT_DIR}\" in the container)")

    files = set()
    for f in entries:
        full = os.path.join(IMAGE_INPUT_DIR, f)
        if os.path.isfile(full) and os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS:
            files.add(full)
    return files


def is_portrait(path: str) -> bool:
    with Image.open(path) as img:
        w, h = img.size
    return h >= w * 1.2  # e.g. portrait if height is at least 20% greater


def classify_new_image(path: str | Path, logger: JobLogger):
    classification = classify_image(path, logger=logger)
    source_image, _ = SourceImage.objects.get_or_create(
        path=str(path),
        defaults={
            "classification": classification.to_dict(),
            "score": calculate_static_score_for_source(classification),
        },
    )
    logger.info(
        f'Image with path "{path}"\nSource image id:{source_image.pk}\nclassification:\n{json.dumps(classification.to_dict(), indent=4)}'
    )


class ClassifyParams(BaseModel):
    max_num_to_classify: Optional[int] = 10


@job_function("classify", ClassifyParams)
def classify_images(
    job: Job, logger: JobLogger, *, max_num_to_classify: Optional[int], **kwargs
):
    if max_num_to_classify and max_num_to_classify <= 0:
        logger.warn("Nothing to do: max_num_to_generate <= 0")
        return
    fs_paths: set[str] = find_files()
    db_paths: set[str] = set(SourceImage.objects.values_list("path", flat=True))

    unprocessed_paths = list(fs_paths - db_paths)
    random.shuffle(unprocessed_paths)

    logger.debug(f"Attempting to classify unprocessed images. max_num_to_classify={max_num_to_classify} len(unprocessed_paths)={len(unprocessed_paths)}\n{',/n'.join(fs_paths)}\n---\n\n{',/n'.join(db_paths)}")

    to_process = unprocessed_paths[:max_num_to_classify]

    if to_process:
        logger.info(
            f"Found {len(unprocessed_paths)} new images. Will classify {len(to_process)} in this run. Specifically: {', '.join(to_process)}"
        )
        for image_path in to_process:
            classify_new_image(image_path, logger, **kwargs)
    else:
        logger.debug("No new images to classify")
