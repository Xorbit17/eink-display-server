from django.contrib import admin
from dashboard.models.photos import SourceImage, Variant
from dashboard.models.job import Job, Execution, JobLogEntry
from dashboard.models.weather import Location, WeatherDetail, DayForecast
from dashboard.models.application import MinuteSystemSample, PrerenderedDashboard
from dashboard.models.calendar import CalendarSource, CalendarOccurrence
from dashboard.models.schedule import Display, WeeklyRule
from dashboard.models.art import Artstyle, ArtstyleContentType, ContentType
from solo.admin import SingletonModelAdmin
from .models.app_settings import AppSettings

@admin.register(SourceImage)
class SourceImageAdmin(admin.ModelAdmin):
    list_display = [f.name for f in SourceImage._meta.fields]
    search_fields = ("path",)
    readonly_fields = ("created_at", "updated_at")

@admin.register(Variant)
class RenderedAssetAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Variant._meta.fields]
    list_filter = ("art_style","content_type","photorealist","favorite","source_quality")
    search_fields = ("path", "art_style",)
    readonly_fields = ("source_image", "created_at", "updated_at")
@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Job._meta.fields]
    list_filter = ("enabled", "job_function_name", "last_run_status")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")

@admin.register(Execution)
class ExecutionAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Execution._meta.fields]
    list_filter = ("status",)
    search_fields = ("job__name", "summary")
    readonly_fields = ("created_at", "updated_at","job","started_at","finished_at","runtime_ms","summary","error","params")


@admin.register(JobLogEntry)
class JobLogEntryAdmin(admin.ModelAdmin):
    list_display = ["execution","ts","level","message","context","seq","created_at"]
    list_filter = ("level",)
    search_fields = ("message",)
    readonly_fields = ["execution","ts","level","message","context","seq","created_at"]

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Location._meta.fields]
    search_fields = ["name"]  # adjust if you have a name/label field


@admin.register(DayForecast)
class DayForecastAdmin(admin.ModelAdmin):
    list_display = [f.name for f in DayForecast._meta.fields]
    readonly_fields = ("created_at", "updated_at")
    search_fields = ["location__id", "date"]
    list_filter = ["location", "date", "generated_at"]


@admin.register(WeatherDetail)
class WeatherDetailAdmin(admin.ModelAdmin):
    list_display = [f.name for f in WeatherDetail._meta.fields]

@admin.register(MinuteSystemSample)
class MinsystemSampleAdmin(admin.ModelAdmin):
    list_display = [f.name for f in MinuteSystemSample._meta.fields]

@admin.register(CalendarSource)
class CalendarSourceAdmin(admin.ModelAdmin):
    list_display = [f.name for f in CalendarSource._meta.fields]
    readonly_fields = ("created_at", "updated_at")

@admin.register(CalendarOccurrence)
class CalendarOccurenceAdmin(admin.ModelAdmin):
    list_display = [f.name for f in CalendarOccurrence._meta.fields]
    readonly_fields = ("created_at", "updated_at")

@admin.register(PrerenderedDashboard)
class PrerenderedDashboardAdmin(admin.ModelAdmin):
    list_display = [f.name for f in PrerenderedDashboard._meta.fields]
    readonly_fields = ("created_at", "updated_at")

@admin.register(Display)
class DisplayAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Display._meta.fields]
    readonly_fields = ("created_at", "updated_at")

@admin.register(WeeklyRule)
class WeeklyRuleAdmin(admin.ModelAdmin):
    list_display = [f.name for f in WeeklyRule._meta.fields]
    readonly_fields = ("created_at", "updated_at")

@admin.register(Artstyle)
class ArtstyleAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Artstyle._meta.fields]
    readonly_fields = ("created_at", "updated_at")

@admin.register(ArtstyleContentType)
class ArtstyleContentTypeAdmin(admin.ModelAdmin):
    list_display = [f.name for f in ArtstyleContentType._meta.fields]

@admin.register(ContentType)
class ContentTypeAdmin(admin.ModelAdmin):
    list_display = [f.name for f in ContentType._meta.fields]
    readonly_fields = ("created_at", "updated_at")

@admin.register(AppSettings)
class AppSettingsAdmin(SingletonModelAdmin):
    pass
