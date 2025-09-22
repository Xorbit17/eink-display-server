from __future__ import annotations
from django.template import Engine, Context
from dashboard.server_types import BaseLogger
from dashboard.models.photos import SourceImage
from dashboard.models.art import ContentType
from dashboard.services.app_settings import settings
from dashboard.jobs.job_registry import JobErrorException
from dashboard.services.openai import openai_client
from dashboard.constants import (
    IMAGE_EXTENSIONS,
    MIME_BY_EXT,
)
from dashboard.services.image_processing import file_to_base64
from pathlib import Path
from typing import cast

from dashboard.services.openai_prompting import (
    GenericArtStyleChoices,
    render_md_prompt,
    get_artstyles_for_content_type,
    get_artstyle_choices_model
)

import json

CHOOSE_ART_STYLE_TEMPLATE = (
    Path(__file__).resolve().parent.parent / "context-templates" / "choose-art-style.md"
).read_text()

def choose_art_style(source: SourceImage, *, logger: BaseLogger):
    if not openai_client:
        raise Exception("OpenAI key not provided")
    if not source.classification:
        raise Exception("choose_art_style requires a source image with a classification")
    p = Path(source.path)
    ext = p.suffix.lower()
    if ext not in IMAGE_EXTENSIONS:
        raise ValueError(
            f"Unsupported image extension: {ext}. Supported: {sorted(IMAGE_EXTENSIONS)}"
        )
    mime = MIME_BY_EXT.get("jpg") if ext == "heic" else MIME_BY_EXT.get(ext)
    image_b64 = file_to_base64(p)
    content_type_record = ContentType.objects.get(name=source.classification["contentType"])
    context = Context({
        "classification": json.dumps(source.classification, indent=4),
        "content_type_prompt": content_type_record.generator_prompt,
        "art_styles": list(get_artstyles_for_content_type(content_type_record).values()),
    })

    prompt = render_md_prompt(CHOOSE_ART_STYLE_TEMPLATE, context)
    logger.debug(f"Art selection prompt prompt:\n---\n{prompt}")
    text_format = get_artstyle_choices_model(content_type_record)

    response = openai_client.responses.parse(
        model=settings().image_classification_model,
        text_format=text_format,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt,
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:{mime};base64,{image_b64}",
                        "detail": "high",
                    },
                ],
            }
        ],
    )

    if response.output_parsed is None:
        raise JobErrorException("Classification function did not succeed")
    
    return response.output_parsed



