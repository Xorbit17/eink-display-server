from __future__ import annotations
from django.template import Engine, Context
from django.db.models import QuerySet
from dashboard.constants import (
    QualityClassification,
    RenderDecision,
)
from dashboard.models.art import ContentType, Artstyle
from pydantic import BaseModel, Field
from typing import Literal, Mapping, Any, Union, Iterable, List
from functools import lru_cache
from dataclasses import dataclass, asdict

@lru_cache(maxsize=1)
def get_artstyles_for_content_type(content_type: Union[ContentType, int, str]) -> QuerySet[Artstyle]:
    if isinstance(content_type, ContentType):
        content_type_record = content_type
    elif isinstance(content_type, int):
        content_type_record = ContentType.objects.get(pk=content_type)
    else:
        content_type_record = ContentType.objects.get(name=content_type)

    return Artstyle.objects.filter(artstylecontenttype__content_type=content_type_record).distinct().order_by("-score", "name")

def get_artstyle_names(content_type: Union[ContentType, int, str], artstyles: Iterable[Artstyle] | None = None):
    if artstyles is None:
        artstyles = get_artstyles_for_content_type(content_type)
    return [a.name for a in artstyles]

def get_content_type_names() -> tuple[str, ...]:
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

def get_artstyle_choices_model(content_type: Union[ContentType, int, str]) -> type[BaseModel]:
    if isinstance(content_type, ContentType):
        content_type_record = content_type
    elif isinstance(content_type, int):
        content_type_record = ContentType.objects.get(pk=content_type)
    else:
        content_type_record = ContentType.objects.get(name=content_type)
    names = get_artstyle_names(content_type_record)
    ArtStyleLiteral = Literal[("CATCH_ALL",)] if not names else Literal[*names]

    class ArtStyleChoice(BaseModel):
        name: ArtStyleLiteral # type: ignore
        motivation: str
        context: str

    class ArtStyleChoices(BaseModel):
        styles: List[ArtStyleChoice]

    return ArtStyleChoices

@dataclass
class GenericArtStyleChoice:
    name: str
    motivation: str
    context: str

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "GenericArtStyleChoice":
        return cls(
            name=data["name"],
            motivation=data["motivation"],
            context=data["context"]
        )

@dataclass
class GenericArtStyleChoices:
    styles: List[GenericArtStyleChoice]

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "GenericArtStyleChoices":
        return cls(
            styles=[GenericArtStyleChoice.from_dict(d) for d in data["styles"]]
        )


_engine = Engine([], autoescape=False)


def render_md_prompt(md_text: str, context: Context) -> str:
    template = _engine.from_string(md_text)
    return template.render(context)
