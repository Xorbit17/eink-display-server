from django.apps import AppConfig
import pillow_heif

pillow_heif.register_heif_opener()

class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'

    def ready(self) -> None:
        return super().ready()
