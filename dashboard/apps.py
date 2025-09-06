from django.apps import AppConfig
from pi_heif import register_heif_opener

register_heif_opener()

class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'

    def ready(self) -> None:
        return super().ready()
