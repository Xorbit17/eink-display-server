from django.urls import path
from dashboard.views.dashboard import DashboardView
from dashboard.views.home import HomeView
from dashboard.views.photo import PhotoView
from dashboard.views.display_service import DisplayDashboardView, DisplayVariantView, DisplayBootScreenView
from dashboard.views.info_screens import BootScreenView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),  # matches "/"
    path("dashboard", DashboardView.as_view(), name="dashboard"),
    path("photo", PhotoView.as_view(), name="photo"),
    path("bootstrap", BootScreenView.as_view(), name="bootstrap"),
    # path("api/display/json/", DisplayJsonView.as_view(), name="display-json"),
    path("api/display/variant", DisplayVariantView.as_view(), name="display-image"),
    path("api/display/dashboard", DisplayDashboardView.as_view(), name="display-image"),
    path("api/display/bootstrap", DisplayBootScreenView.as_view(), name="display-bootstrap"),
]
