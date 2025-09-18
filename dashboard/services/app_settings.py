from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import connection
from django.db.utils import OperationalError, ProgrammingError

if TYPE_CHECKING:  # Only used for type checking to avoid import-time side effects
    from ..models.app_settings import AppSettings


def settings() -> "AppSettings":
    """
    Returns AppSettings if the table exists; otherwise a lightweight object with defaults.
    Never call models at import time outside this function.
    """
    try:
        if "dashboard_appsettings" not in connection.introspection.table_names():
            return _default_settings() # type: ignore

        from ..models.app_settings import AppSettings
        return AppSettings.get_solo()
    except (OperationalError, ProgrammingError):
        return _default_settings() # type: ignore

def _default_settings():
    class Defaults:
        setup_completed = False
        discovery_port = 51234
        openai_key = None
        openweathermap_key = None
        image_art_generation_model = "gpt-5"
        image_classification_model = "gpt-5"
        image_source_dir = "<Settings not ready>"
        image_generation_dir = "<Settings not ready>"

    return Defaults()
