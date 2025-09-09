from .pipeline_registry import ImageProcessingContext, pipeline_function
from PIL import Image
from pathlib import Path
from django.template import Context
from django.core.exceptions import ObjectDoesNotExist
from dashboard.models.art import ContentType, Artstyle
from dashboard.services.openai import openai_client
from dashboard.services.image_processing import pil_to_base64, base64_to_pil
from pydantic import BaseModel

from dashboard.services.openai_prompting import (
    render_md_prompt,
)

ART_GENERATOR_PROMPT_TEMPLATE = (
    Path(__file__).resolve().parent.parent
    / "context-templates"
    / "image-artstyle-applicator.md"
).read_text()


class OpenAiProcessParameters(BaseModel):
    art_style: str


@pipeline_function("openai_filter")
def openai_process(
    image: Image.Image, context: ImageProcessingContext, /, art_style: str
) -> Image.Image:
    if not openai_client:
        raise Exception("OpenAI key not provided")
    if not context.classification:
        raise Exception("Context does not contain classification")
    has_alpha = image.mode in ("RGBA", "LA", "P") and (
        "A" in image.getbands() or "transparency" in image.info
    )
    if has_alpha:
        raise Exception("Images with alpha are not supported")
    try:
        content_type = ContentType.objects.get(name=context.classification.contentType)
    except ObjectDoesNotExist:
        raise Exception(
            f"Content type '{context.classification.contentType}' not found in database"
        )
    artstyle_record = Artstyle.objects.get(name=art_style)
    prompt_context = Context(
        {
            "content_type": content_type.name,
            "content_type_prompt": content_type.generator_prompt,
            "art_style": artstyle_record.name,
            "artstyle_prompt": artstyle_record.generator_prompt,
        }
    )
    prompt = render_md_prompt(ART_GENERATOR_PROMPT_TEMPLATE, prompt_context)
    context.logger.debug(f"AI generator prompt:\n---\n{prompt}")
    b64 = pil_to_base64(image)

    # TODO error handling?
    response = openai_client.responses.create(
        model="gpt-5",
        stream=False,
        tools=[{"type": "image_generation"}],
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{b64}",
                        "detail": "high",
                    },
                ],
            }
        ],
    )
    image_data = [
        output.result
        for output in response.output
        if output.type == "image_generation_call"
    ]
    if image_data[0]:
        return base64_to_pil(image_data[0])

    raise Exception("OpenAI did not return an image format.")
