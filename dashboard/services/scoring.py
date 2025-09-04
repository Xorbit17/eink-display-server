from dashboard.jobs.image_processing_declaration import (
    NOT_SUITED,
    BAD,
    PASSABLE,
    GOOD,
    VERY_GOOD,
    PERSON,
    PEOPLE,
    ANIMAL,
    LANDSCAPE,
    CITY,
    BUILDING,
    NATURE,
    ART,
    OBJECT,
    OTHER,
    
)
from typing import Dict
from django.utils import timezone
from datetime import datetime
from math import exp, log

QUALITY_MAP: Dict[str,float] = {
    NOT_SUITED: 0.0,
    BAD: 0.2,
    PASSABLE :0.5,
    GOOD: 0.8,
    VERY_GOOD: 0.95,
}

CONTENT_TYPE_MAP: Dict[str, float] = {
    PERSON: 0.5,
    PEOPLE: 0.5,
    ANIMAL: 0.5,
    LANDSCAPE: 0.5,
    CITY: 0.5,
    BUILDING: 0.5,
    NATURE: 0.5,
    ART: 0.5,
    OBJECT: 0.5,
    OTHER: 0.5,
}

# 0.5 is Neutral preference (>0.5 for pro-photo, <0.5 for pro-art)
PHOTOREALIST_SCORE: float = 0.5

Q_FACTOR = 1.0
C_FACTOR = 0.5
P_FACTOR = 0.5

# How strongly "favourite" should influence the final score (0..1, normalized inside).
FAVOURITE_FACTOR: float = 0.75

# How strongly "date/novelty" should influence the final score (0..1, normalized inside).
DATE_FACTOR: float = 0.75

# Map the favourite boolean to a score in [0..1].
# With 0.5 it's neutral; increase to >0.5 to give favourites a boost.
FAVOURITE_SCORE: float = 0.75

# Novelty curve: half-life (in days) controls how fast the boost decays.
NOVELTY_HALF_LIFE_DAYS: float = 14.0

# Minimum novelty value as items age (never demote to zero).
NOVELTY_FLOOR: float = 0.30

def calculate_static_score(
    quality: str,
    content_type: str,
    photorealist: bool,
) -> float:
    """
    Weighted geometric mean of (quality, content, photorealism-preference).
    Returns a value in [0, 1].
    """
    q_score = QUALITY_MAP.get(quality, 0.5)
    c_score = CONTENT_TYPE_MAP.get(content_type, 0.5)
    p_score = PHOTOREALIST_SCORE if photorealist else (1.0 - PHOTOREALIST_SCORE)

    # Normalize factors -> weights
    factors = [Q_FACTOR, C_FACTOR, P_FACTOR]
    total = sum(factors) or 1.0
    weights = [f / total for f in factors]

    epsilon = 1e-6
    s = 1.0
    for val, w in zip((q_score, c_score, p_score), weights):
        s *= max(min(val, 1.0), epsilon) ** w

    return s

def calculate_final_score(
    static_score: float,
    favourite: bool,
    created_at: datetime,
) -> float:
    """
    Weighted geometric mean of:
      - static_score (already in [0,1])
      - favourite score (boost if favourite=True)
      - novelty score based on recency (decays with half-life, floors at NOVELTY_FLOOR)

    Returns a float in [0,1].
    """
    # 1) Favourite -> score in [0,1]
    fav_score = FAVOURITE_SCORE if favourite else (1.0 - FAVOURITE_SCORE)

    # 2) Novelty -> score in [NOVELTY_FLOOR, 1]
    now = timezone.now()
    age_seconds = max((now - created_at).total_seconds(), 0.0)
    age_days = age_seconds / 86400.0

    # Exponential decay to a floor: 1 at t=0, approaches NOVELTY_FLOOR as t grows.
    decay = exp(-log(2) * (age_days / max(NOVELTY_HALF_LIFE_DAYS, 1e-6)))
    novelty_score = NOVELTY_FLOOR + (1.0 - NOVELTY_FLOOR) * decay

    # 3) Weighted geometric mean of (static, favourite, novelty)
    #    We give "static" an implicit base weight of 1.0 so you only tune the extras.
    factors = [1.0, FAVOURITE_FACTOR, DATE_FACTOR]
    total = sum(factors)
    weights = [f / total for f in factors]

    # Clamp to avoid log(0) behaviour and keep everything in [0,1]
    epsilon = 1e-6
    s = 1.0
    for val, w in zip(
        (max(min(static_score, 1.0), epsilon),
         max(min(fav_score, 1.0), epsilon),
         max(min(novelty_score, 1.0), epsilon)),
        weights,
    ):
        s *= val ** w

    return max(0.0, min(s, 1.0))