from __future__ import annotations
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
    get_content_type_prompt_context,
    get_classification_model,
    render_md_prompt,
    GenericImageClassification,
)

CLASSIFY_PROMPT_TEMPLATE = (
    Path(__file__).resolve().parent.parent / "context-templates" / "image-classifier.md"
).read_text()


def classify_image(path: str | Path) -> GenericImageClassification:
    """
    Upload an image and ask OpenAI to classify its suitability for e-ink portrait generation.
    Returns the model's text response.
    """
    if not openai_client:
        raise Exception("OpenAI key not provided")
    p = Path(path)
    ext = p.suffix.lower()
    if ext not in IMAGE_EXTENSIONS:
        raise ValueError(
            f"Unsupported image extension: {ext}. Supported: {sorted(IMAGE_EXTENSIONS)}"
        )
    # file_to_base64 automatically converts HEIC to JPG
    mime = MIME_BY_EXT.get("jpg") if ext == "heic" else MIME_BY_EXT.get(ext)
    image_b64 = file_to_base64(p)
    prompt = render_md_prompt(CLASSIFY_PROMPT_TEMPLATE, get_content_type_prompt_context())
    text_format = get_classification_model()

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
    
    return cast(GenericImageClassification,response.output_parsed.model_dump())
