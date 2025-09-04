from __future__ import annotations

import os
import random

from dashboard.models.job import Job
from dashboard.models.photos import SourceImage
from dashboard.services.logger_job import RunLogger
from dashboard.constants import (
    IMAGE_DIR,
    IMAGE_EXTENSIONS,
)
from dashboard.services.classify_image import classify_image
from dashboard.jobs.job_registry import register
from PIL import Image
import json


def find_files() -> set[str]:
    """Return absolute paths of images in IMAGE_DIR (no subdirs)."""
    try:
        entries = os.listdir(IMAGE_DIR)
    except FileNotFoundError:
        return set()

    files = set()
    for f in entries:
        full = os.path.join(IMAGE_DIR, f)
        if os.path.isfile(full) and os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS:
            files.add(full)
    return files


def is_portrait(path: str) -> bool:
    with Image.open(path) as img:
        w, h = img.size
    return h >= w * 1.2  # e.g. portrait if height is at least 20% greater

def classify_new_image(path: str, logger: RunLogger, params: dict | None):
    classification = None
    try:
        classification = classify_image(path)
    except Exception as e:
        logger.error(f"Classification of image with path \"{path}\" failed. OpenAI error.\n{json.dumps(e)}")
        return
    if classification is None:
        return
    serialisable_classification = classification.model_dump()
    source_image, _ = SourceImage.objects.get_or_create(
        path=path,
        classification=serialisable_classification,
        has_variants=False,
    )
    logger.info(f"Image with path \"{path}\"\nSource image id:{source_image.pk}\nclassification:\n{json.dumps(serialisable_classification, indent=4)}")


@register("CLASSIFY")
def classify_images(job: Job, logger: RunLogger, params: dict | None):
    max_num_to_classify = int((params or {}).get("max_num_to_classify", 1))
    if max_num_to_classify <= 0:
        logger.warn("Nothing to do: max_num_to_generate <= 0")
        return
    fs_paths: set[str] = find_files()
    db_paths: set[str] = set(SourceImage.objects.values_list("path", flat=True))

    unprocessed_paths = list(fs_paths - db_paths)
    random.shuffle(unprocessed_paths)

    to_process = unprocessed_paths[:max_num_to_classify]

    if to_process:
        logger.info(
            f"Found {len(unprocessed_paths)} new images. Will classify {len(to_process)} in this run. Specifically: {', '.join(to_process)}"
        )
        for image_path in to_process:
            classify_new_image(image_path, logger, params=params)
    else:
        logger.debug(
            f"No new images to classify"
        ) 
    
