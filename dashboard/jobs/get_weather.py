from dashboard.jobs.job_registry import register
from dashboard.services.logger_job import RunLogger
from time import sleep
from django.utils import timezone
from dashboard.models.weather import DayForecast, Location, WeatherDetail
import dashboard.services.get_weather as weather_service
from dashboard.services.util import convert_unix_dt_to_datetime, local_date
import datetime
from dataclasses import dataclass

@dataclass
class Context:
    now: datetime.datetime



def process_record(input: weather_service.DailyItem, location: Location, context: Context):
    generated_at = context.now

    date_local = local_date(convert_unix_dt_to_datetime(input.dt))
    defaults = {
        "generated_at": generated_at,

        # temps
        "temp_day": input.temp.day,
        "temp_min": input.temp.min,
        "temp_max": input.temp.max,
        "temp_night": input.temp.night,
        "temp_eve": input.temp.eve,
        "temp_morn": input.temp.morn,

        # feels_like
        "feels_day": input.feels_like.day,
        "feels_night": input.feels_like.night,
        "feels_eve": input.feels_like.eve,
        "feels_morn": input.feels_like.morn,

        # atmosphere / wind
        "pressure": input.pressure,
        "humidity": input.humidity,
        "dew_point": input.dew_point,
        "wind_speed": input.wind_speed,
        "wind_deg": input.wind_deg,
        "wind_gust": getattr(input, "wind_gust", None),

        # clouds, UV, precip probability/amounts
        "clouds": input.clouds,
        "uvi": input.uvi,
        "precipitation_probability": input.pop,
        "rain": getattr(input, "rain", None),
        "snow": getattr(input, "snow", None),
    }

    day_forecast, _created = DayForecast.objects.update_or_create(
        location=location,
        date=date_local,
        defaults=defaults,
    )

    for weather_detail in input.weather:
        defaults = {
            "weather_id": weather_detail.id,
            "main_type": weather_detail.main,
            "description": weather_detail.description
        }
        WeatherDetail.objects.update_or_create(
            day_forecast=day_forecast,
            defaults=defaults,
        )
    return day_forecast


@register('WEATHER')
def get_weather(_, logger: RunLogger, params):
    now = timezone.now()
    locations = Location.objects.all()
    for location in locations:
        logger.info(f"Getting weather for {location.name}")
        weatherData = weather_service.get_weather((location.latitude, location.longitude))

        for record in weatherData.daily:
            process_record(record, location, context=Context(now=now))






