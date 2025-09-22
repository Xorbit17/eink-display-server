from django.urls import path
from dashboard.views.dashboard import DashboardView
from dashboard.views.home import HomeView
from dashboard.views.photo import PhotoView
from dashboard.views.display_service import (
    DisplayDashboardView,
    DisplayVariantView,
    DisplayBootScreenView,
    DisplayButtonController,
    DisplayPollController,
    BootstrapController,
    DisplayPaletteView,
)
from dashboard.views.info_screens import BootScreenView
from dashboard.views.health import HealthView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),  # matches "/"
    path("dashboard", DashboardView.as_view(), name="dashboard"),
    path("health", HealthView.as_view(), name="health"),
    path("photo", PhotoView.as_view(), name="photo"),
    path("bootstrap", BootScreenView.as_view(), name="bootstrap"),
    path("api/display/variant", DisplayVariantView.as_view(), name="display-image"),
    path("api/display/dashboard", DisplayDashboardView.as_view(), name="display-image"),
    path(
        "api/display/splash_screen",
        DisplayBootScreenView.as_view(),
        name="display-bootstrap",
    ),
    path(
        "api/display/button", DisplayButtonController.as_view(), name="display-button"
    ),
    path("api/display/poll", DisplayPollController.as_view(), name="display-poll"),
    path(
        "api/display/bootstrap", BootstrapController.as_view(), name="display-bootstrap"
    ),
    path("api/display/palette", DisplayPaletteView.as_view(), name="display-palette"),
]
