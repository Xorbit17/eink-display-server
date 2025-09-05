from __future__ import annotations
from django.template import Engine, Context
from dashboard.constants import (
    QualityClassification,
    RenderDecision,
)
from dashboard.models.art import ContentType
from pydantic import BaseModel
from typing import Literal
from functools import lru_cache
from dataclasses import dataclass


@lru_cache(maxsize=1)
def get_content_type_names() -> tuple[str, ...]:
    # return a stable tuple for Literal unpacking
    return tuple(ContentType.objects.order_by("name").values_list("name", flat=True))


@lru_cache(maxsize=1)
def get_content_type_prompt_context() -> Context:
    return Context(
        {
            "content_types": list(
                ContentType.objects.order_by("name").values_list(
                    "name", "classifier_prompt"
                )
            )
        }
    )

@dataclass
class GenericImageClassification:
    quality: QualityClassification
    contentType: str
    renderDecision: RenderDecision
    portrait: bool
    peopleCount: int
    portraitSuitable: bool
    photoRealistic: bool
    cartoony: bool
    art: bool
    descriptionOfImage: str
    qualityClassificationExplanation: str

def get_classification_model() -> type[BaseModel]:
    names = get_content_type_names()
    ContentTypeLiteral = Literal[("CATCH_ALL",)] if not names else Literal[*names]

    class ImageClassification(BaseModel):
        quality: QualityClassification
        contentType: ContentTypeLiteral  # type: ignore
        renderDecision: RenderDecision
        portrait: bool
        peopleCount: int
        portraitSuitable: bool
        photoRealistic: bool
        cartoony: bool
        art: bool
        descriptionOfImage: str
        qualityClassificationExplanation: str

    return ImageClassification


_engine = Engine([], autoescape=False)


def render_md_prompt(md_text: str, context: Context) -> str:
    template = _engine.from_string(md_text)
    return template.render(context)
