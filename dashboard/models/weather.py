from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class WeatherDetail(models.Model):
    day_forecast = models.ForeignKey(
        "DayForecast",
        on_delete=models.CASCADE,
        related_name="weather_details",
        db_index=True,
    )
    weather_id = models.IntegerField(null=True, blank=True)  # API's numeric id
    main_type = models.CharField(max_length=40)
    description = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return f"{self.main_type or '—'}"

class Location(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    latitude = models.CharField(max_length=20)
    longitude = models.CharField(max_length=20)

    def __str__(self): return self.name
class DayForecast(models.Model):
    location = models.ForeignKey("Location", on_delete=models.CASCADE)

    date = models.DateField(db_index=True)
    generated_at = models.DateTimeField(db_index=True)

    # temps
    temp_day = models.FloatField()
    temp_min = models.FloatField()
    temp_max = models.FloatField()
    temp_night = models.FloatField()
    temp_eve = models.FloatField()
    temp_morn = models.FloatField()

    # feels_like
    feels_day = models.FloatField()
    feels_night = models.FloatField()
    feels_eve = models.FloatField()
    feels_morn = models.FloatField()

    # atmosphere / wind
    pressure = models.IntegerField()
    humidity = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    dew_point = models.FloatField()
    wind_speed = models.FloatField()
    wind_deg = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(360)])
    wind_gust = models.FloatField(null=True, blank=True)

    # clouds, UV, precip probability/amount
    clouds = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    uvi = models.FloatField()
    precipitation_probability = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])  # 0..1
    rain = models.FloatField(null=True, blank=True)  # mm (may be absent)
    snow = models.FloatField(null=True, blank=True)  # mm (may be absent)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["location", "date", "generated_at"],
                name="uniq_day_forecast_per_run"
            )
        ]
        indexes = [
            models.Index(fields=["location", "date"]),
        ]

    def __str__(self):
        return f"{self.location} • {self.date} (gen {self.generated_at})"
