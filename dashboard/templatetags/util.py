from django import template
from django.utils.timezone import localtime

register = template.Library()

@register.filter
def longdate(value):
    """
    Format a datetime as 'Monday 11/08/2025 12:30'.
    Returns empty string if value is None.
    """
    if not value:
        return ""
    value = localtime(value)  # respect TIME_ZONE setting
    return value.strftime("%A %d/%m/%Y %H:%M")

