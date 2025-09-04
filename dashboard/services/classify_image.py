from __future__ import annotations
from dashboard.services.openai import openai_client
from dashboard.constants import (
    IMAGE_DIR,
    IMAGE_EXTENSIONS,
    MIME_BY_EXT,
)
from dashboard.jobs.image_processing_declaration import (
    ContentTypeClassification,
    QualityClassification,
    RenderDecision,
)
from dashboard.services.image_processing import file_to_base64
from pathlib import Path
import base64
from pydantic import BaseModel
from openai import BadRequestError


CLASSIFY_PROMPT = (
    Path(__file__).resolve().parent.parent / "context_templates" / "image-classifier.md"
).read_text()

class ImageClassification(BaseModel):
    quality: QualityClassification
    contentType: ContentTypeClassification
    renderDecision: RenderDecision
    portrait: bool
    multiplePersons: bool
    portraitSuitable: bool
    photoRealistic: bool 
    cartoony: bool
    art: bool
    descriptionOfImage: str
    qualityClassificationExplanation: str


def classify_image(path: str) -> ImageClassification | None:
    """
    Upload an image and ask OpenAI to classify its suitability for e-ink portrait generation.
    Returns the model's text response.
    """
    p = Path(path)
    ext = p.suffix.lower()
    if ext not in IMAGE_EXTENSIONS:
        raise ValueError(
            f"Unsupported image extension: {ext}. Supported: {sorted(IMAGE_EXTENSIONS)}"
        )
    # file_to_base64 automatically converts HEIC to JPG
    mime = MIME_BY_EXT.get("jpg") if ext == 'heic' else MIME_BY_EXT.get(ext)
    image_b64 = file_to_base64(p)
    response = openai_client.responses.parse(
        model="gpt-5",
        text_format=ImageClassification,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": CLASSIFY_PROMPT,
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:{mime};base64,{image_b64}",
                        "detail":"high", 
                    },
                ],
            }
        ],
    )
    pass
    return response.output_parsed
