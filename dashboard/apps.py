from django.apps import AppConfig
import os
import importlib

_p_heif = None

def get_heif():
    global _p_heif
    if _p_heif is not None:
        return _p_heif

    env = os.getenv("ENV", "development")
    candidates = ["pillow_heif", "pi_heif"] if env == "development" else ["pi_heif", "pillow_heif"]

    for mod in candidates:
        try:
            _p_heif = importlib.import_module(mod)
            return _p_heif
        except ModuleNotFoundError:
            pass

    raise ImportError("Install either pillow_heif (dev/x86) or pi_heif (Pi).")

p_heif = get_heif()
p_heif.register_heif_opener() # type: ignore

class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'

    def ready(self) -> None:
        return super().ready()
