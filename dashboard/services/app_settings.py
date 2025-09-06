# dashboard/services/app_settings.py
from django.db import connection
from django.db.utils import OperationalError, ProgrammingError

def settings():
    """
    Returns AppSettings if the table exists; otherwise a lightweight object with defaults.
    Never call models at import time outside this function.
    """
    try:
        if "dashboard_appsettings" not in connection.introspection.table_names():
            return _default_settings()

        from ..models import AppSettings
        return AppSettings.get_solo()
    except (OperationalError, ProgrammingError):
        return _default_settings()

def _default_settings():
    class Defaults:
        setup_completed = False
        source_image_dir = "/app/input"
        generate_image_dir = "/app/generate"
        discovery_port = 51234
        openai_key = None
        openweathermap_key = None
        image_art_generation_model = "gpt-5"
        image_classification_model = "gpt-5"
    return Defaults()
