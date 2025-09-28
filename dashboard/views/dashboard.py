from dataclasses import dataclass, asdict
from dashboard.color_constants import PaletteEnum
from django.shortcuts import render
from django.views import View
from django.utils import timezone
from dashboard.views.dashboard_mixins.calendar import (
    CalendarMixin,
    DashboardCalendarView,
)
from dashboard.views.dashboard_mixins.disks import (
    DashboardDisksMixin,
    DashboardDisksView,
)
from dashboard.views.dashboard_mixins.stats import (
    DashboardStatsMixin,
    DashboardStatsView,
)
from dashboard.views.dashboard_mixins.weather import (
    DashboardWeatherMixin,
    DashboardWeatherView,
)
from dashboard.views.dashboard_mixins.header import (
    DashboardHeaderMixin,
    DashboardHeaderView,
)


@dataclass
class DashboardViewData:
    header: DashboardHeaderView | None  # None is not rendered
    weather: DashboardWeatherView | None
    disks: DashboardDisksView | None
    stats: DashboardStatsView | None
    calendar: DashboardCalendarView | None
    css_color_vars: str


class DashboardView(
    View,
    CalendarMixin,
    DashboardDisksMixin,
    DashboardStatsMixin,
    DashboardWeatherMixin,
    DashboardHeaderMixin,
):
    def get(self, request):
        now_minute = timezone.now().replace(second=0, microsecond=0)
        # Get alerts; for now empty list
        view_data = DashboardViewData(
            header=self.get_header(now_minute),
            stats=self.get_stats(now_minute),
            weather=self.get_weather(now_minute),
            disks=self.get_disks(now_minute),
            calendar=self.get_calendar(now_minute),
            css_color_vars=PaletteEnum.NATIVE_EXTENDED_SHADED.to_css_vars()
        )
        return render(request, "dashboard/dashboard.html", context=asdict(view_data))
