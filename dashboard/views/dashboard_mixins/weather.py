from django.db.models import Prefetch
from dashboard.models.weather import DayForecast, Location, WeatherDetail
from dashboard.services.util import local_date
from dashboard.services.get_weather import (
    wind_ms_to_beaufort,
    get_direction_letter_from_wind_dir,
    get_icon_from_code,
)
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List


@dataclass
class WeatherDetailView:
    icon: str
    main: str
    description: str


@dataclass
class WeatherDayView:
    label: str  # "Wednesday" or "Today"
    # temps
    temp_day: str
    temp_min: str
    temp_max: str
    temp_night: str
    temp_eve: str
    temp_morn: str

    # feels_like
    feels_day: str
    feels_night: str
    feels_eve: str
    feels_morn: str
    wind_speed_bft: str
    wind_dir_letters: str
    wind_gust_bft: str | None
    wind_descr: str

    # Other
    cloud_pct: str
    uvi: str
    percipitation_probability_pct: str
    detail: WeatherDetailView


@dataclass
class DashboardWeatherView:
    days: List[WeatherDayView]
    updated_at: datetime


class DashboardWeatherMixin:
    def get_weather(self, now: datetime) -> DashboardWeatherView:
        dates = [local_date(now + timedelta(days=i)) for i in range(6)]
        location = Location.objects.get(name="Blankenberge")
        qs = (
            DayForecast.objects.filter(
                location=location, date__in=set(dates)
            )  # set() dedupes
            .order_by("date")  # or "date","generated_at"
            .prefetch_related(
                Prefetch(
                    "weather_details",
                    queryset=WeatherDetail.objects.all().order_by("id"),
                )
            )
        )

        def make_view(forecast: DayForecast) -> WeatherDayView:
            detail: WeatherDetail = forecast.weather_details.all()[0]  # type: ignore
            return WeatherDayView(
                label=forecast.date.strftime("%A"),
                temp_day=f"{forecast.temp_day:.1f}",
                temp_min=f"{forecast.temp_min:.1f}",
                temp_max=f"{forecast.temp_max:.1f}",
                temp_night=f"{forecast.temp_night:.1f}",
                temp_eve=f"{forecast.temp_eve:.1f}",
                temp_morn=f"{forecast.temp_morn:.1f}",
                # feels_like
                feels_day=f"{forecast.feels_day:.1f}",
                feels_night=f"{forecast.feels_night:.1f}",
                feels_eve=f"{forecast.feels_eve:.1f}",
                feels_morn=f"{forecast.feels_morn:.1f}",
                wind_speed_bft=str(wind_ms_to_beaufort(forecast.wind_speed)[0]),
                wind_dir_letters=get_direction_letter_from_wind_dir(forecast.wind_deg),
                wind_gust_bft=str(
                    wind_ms_to_beaufort(forecast.wind_gust)[0]
                    if forecast.wind_gust is not None
                    else None
                ),
                wind_descr=wind_ms_to_beaufort(forecast.wind_speed)[1],
                # Other
                cloud_pct=str(forecast.clouds),
                uvi=str(forecast.uvi),
                percipitation_probability_pct=str(
                    int(forecast.precipitation_probability * 100.0)
                ),
                detail=WeatherDetailView(
                    main=detail.main_type,
                    description=detail.description.capitalize(),
                    icon=get_icon_from_code(detail.weather_id)
                    if detail.weather_id
                    else "",
                ),
            )

        days: List[WeatherDayView] = [make_view(forecast) for forecast in qs]
        return DashboardWeatherView(
            updated_at=now,
            days=days,
        )
