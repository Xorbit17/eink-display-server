from __future__ import annotations
from django.template import Engine, Context
from dashboard.constants import (
    QualityClassification,
    RenderDecision,
)
from dashboard.models.art import ContentType
from pydantic import BaseModel
from typing import Literal, Mapping, Any
from functools import lru_cache
from dataclasses import dataclass, asdict


@lru_cache(maxsize=1)
def get_content_type_names() -> tuple[str, ...]:
    # return a stable tuple for Literal unpacking
    return tuple(ContentType.objects.order_by("name").values_list("name", flat=True))


@lru_cache(maxsize=1)
def get_content_type_prompt_context() -> Context:
    content_types_list = list(
        ContentType.objects.order_by("name").values("name", "classifier_prompt")
    )
    return Context({"content_types": content_types_list})


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

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        # ensure enums are serialized as str
        d["quality"] = self.quality.value
        d["renderDecision"] = self.renderDecision.value
        return d

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "GenericImageClassification":
        return cls(
            quality=QualityClassification(data["quality"]),
            contentType=data["contentType"],
            renderDecision=RenderDecision(data["renderDecision"]),
            portrait=bool(data["portrait"]),
            peopleCount=int(data["peopleCount"]),
            portraitSuitable=bool(data["portraitSuitable"]),
            photoRealistic=bool(data["photoRealistic"]),
            cartoony=bool(data["cartoony"]),
            art=bool(data["art"]),
            descriptionOfImage=str(data["descriptionOfImage"]),
            qualityClassificationExplanation=str(data["qualityClassificationExplanation"]),
        )


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
