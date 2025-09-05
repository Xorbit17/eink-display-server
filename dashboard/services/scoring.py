from typing import Dict, Iterable, List
from django.utils import timezone
from datetime import datetime
from math import exp, log
from dashboard.constants import QualityClassification, RenderDecision
from dashboard.models.art import ContentType
from dashboard.models.photos import SourceImage
from dashboard.services.openai_prompting import GenericImageClassification
import random
from bisect import bisect

QUALITY_MAP: Dict[QualityClassification,float] = {
    QualityClassification.NOT_SUITED: 0.0,
    QualityClassification.BAD: 0.2,
    QualityClassification.PASSABLE :0.4,
    QualityClassification.GOOD: 0.7,
    QualityClassification.VERY_GOOD: 0.95,
}

# 0.5 is Neutral preference (>0.5 for pro-photo, <0.5 for pro-art)
PHOTOREALIST_SCORE = 0.5

# Relative importance of 
Q_FACTOR = 1.0 # Quality
C_FACTOR = 0.5 # Content type
P_FACTOR = 0.5 # Photorealism

# How strongly "date/novelty" should influence the final score (0..1, normalized inside).
DATE_FACTOR = 0.8

HAS_VARIANT_FACTOR = 0.8

# Map the favorite boolean to a score in [0..1].
# With 0.5 it's neutral; increase to >0.5 to give favorites a boost.
FAVORITE_SCORE = 0.75
FAVORITE_FACTOR = 0.75

# Novelty curve: half-life (in days) controls how fast the boost decays.
NOVELTY_HALF_LIFE_DAYS = 14

# Minimum novelty value as items age (never demote to zero).
NOVELTY_FLOOR = 0.30

epsilon = 1e-6

def clamp(x: float) -> float:
    return max(epsilon, min(x, 1.0))

def weighted_geometric_mean(a: Iterable[float], factors:Iterable[float]) -> float:
    total = sum(factors) or 1.0
    weights = [f / total for f in factors]
    acc = 1.0
    for x, w in zip(a, weights):
        acc *= max(min(x, 1.0), epsilon) ** w
    return clamp(acc)

def calculate_static_score_for_source(
    classification: GenericImageClassification,
) -> float:
    """
    Weighted geometric mean of (quality, content, photorealism-preference).
    Returns a value in [0, 1].
    """
    photorealist = True
    if classification.art or classification.cartoony:
        photorealist = False
    
    q_score = QUALITY_MAP.get(classification.quality, 0.5)
    c_score = ContentType.objects.get(name=classification.contentType).score
    p_score = PHOTOREALIST_SCORE if photorealist else (1.0 - PHOTOREALIST_SCORE)

    return weighted_geometric_mean((q_score, c_score, p_score),(Q_FACTOR, C_FACTOR, P_FACTOR))

def calculate_final_score_for_source(
    source_img: SourceImage,
) -> float:
    fav_score = FAVORITE_SCORE if source_img.favorite else (1.0 - FAVORITE_SCORE)

    now = timezone.now()
    age_seconds = max((now - source_img.created_at).total_seconds(), 0.0)
    age_days = age_seconds / 86400.0

    variant_score = 0.3 if source_img.has_variants() else 0.7

    # Exponential decay to a floor: 1 at t=0, approaches NOVELTY_FLOOR as t grows.
    decay = exp(-log(2) * (age_days / max(NOVELTY_HALF_LIFE_DAYS, 1e-6)))
    novelty_score = NOVELTY_FLOOR + (1.0 - NOVELTY_FLOOR) * decay
    scores = [clamp(source_img.score), fav_score, clamp(novelty_score), variant_score]
    factors = [1.0, FAVORITE_FACTOR, DATE_FACTOR, HAS_VARIANT_FACTOR]

    # We give "static" an implicit base weight of 1.0 so we only tune the extras.
    return weighted_geometric_mean(scores,factors)

def select_random_sources(items: list[SourceImage], max_to_select: int) -> list[SourceImage]:
    pick_list = [
        {"source": s, "score": max(0.0, float(calculate_final_score_for_source(s) or 0.0))}
        for s in items
    ]
    weights = [x["score"] for x in pick_list]
    n = min(len(pick_list), max_to_select)

    if not any(weights):
        return []

    chosen = random.choices(pick_list, weights=weights, k=n)
    return [c["source"] for c in chosen]

# TODO select variant based on novelty etc
