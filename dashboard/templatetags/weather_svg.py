from django import template
from django.contrib.staticfiles import finders
from django.utils.safestring import mark_safe
from pathlib import Path
from typing import Literal, Dict
import re

register = template.Library()

IconSize = Literal["LARGE", "MEDIUM", "SMALL","EXTRA_SMALL"]

size_map: Dict[IconSize,int] = {
    'LARGE': 128,
    'MEDIUM': 96,
    'SMALL': 64,
    'EXTRA_SMALL': 32

}

@register.simple_tag
def weather_svg(icon_name: str, size: IconSize='LARGE'):
    """
    Usage: {% weather_icon forecast.icon "wicon wicon-96 text-blue" %}
    """
    size_px = size_map.get(size)
    if not icon_name:
        return "<!-- weather_icon: empty icon name -->"
    rel_path = f"static/svg/weather-bas/{icon_name}"
    data = f'<img src="{rel_path}" alt="{icon_name}" width="{size_px}" height="{size_px}">'
    return mark_safe(data)
