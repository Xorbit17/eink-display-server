

from django.utils import timezone


from dashboard.services.scoring import calculate_final_score
from dashboard.models.photos import Variant
from typing import Iterable, List, Tuple
import os
import random
import mimetypes
from bisect import bisect

def _weighted_choice(items: Iterable[Tuple[Variant, float]]) -> Variant:
    """
    Select a Variant using weighted random by score.
    Expects (variant, weight) pairs with weight >= 0.
    """
    variants: List[Variant] = []
    cumulative: List[float] = []
    total = 0.0

    for v, w in items:
        if w <= 0.0:
            continue
        total += w
        variants.append(v)
        cumulative.append(total)

    if total == 0.0 or not variants:
        raise Exception("No displayable images with positive score.")

    r = random.random() * total
    idx = bisect(cumulative, r)
    return variants[idx]

def get_variant():
    qs = Variant.objects.only(
        "id", "path", "score", "favourite", "created_at"
    ).filter(path__isnull=False).order_by("-score")[:10000]
    if not qs.exists():
        raise Exception("No images available.")
    

    now = timezone.now()
    pairs: List[Tuple[Variant, float]] = []
    for v in qs.iterator():
        # v.score is your persisted static score
        final_score = calculate_final_score(
            static_score=float(v.score or 0.0),
            favourite=bool(v.favourite),
            created_at=v.created_at,
        )
        pairs.append((v, final_score))

    return _weighted_choice(pairs)

