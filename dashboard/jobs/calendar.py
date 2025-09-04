from dashboard.jobs.job_registry import register
from dashboard.services.logger_job import RunLogger
from pydantic import BaseModel, PositiveInt
from typing import Optional
import dashboard.services.get_calendar as service
from django.utils import timezone
from datetime import timedelta
from dashboard.models.calendar import CalendarOccurrence, CalendarSource
from dashboard.constants import LOCAL_TZ, ICAL_GOOGLE_CALENDAR_URL
from django.db import transaction

class CalendarJobParams(BaseModel):
    days_ahead: Optional[int] = None


@register('CALENDAR', CalendarJobParams)
def get_calendar(_, logger: RunLogger, params=CalendarJobParams):
    logger.info("Starting calendar job")
    start = timezone.now()
    start_day = start.replace(minute=0, hour=0)

    end = start_day + timedelta(params.days_ahead) if params.days_ahead is not None else None

    sources = CalendarSource.objects.filter(active=True)

    for source in sources:
        with transaction.atomic():
            for e in service.get_calendar(source.ics_url, start_day,end):
                CalendarOccurrence.objects.update_or_create(
                    source=source,
                    uid=e.uid,
                    instance_start=e.begin.datetime,
                    defaults={
                        "instance_end": e.end.datetime,
                        'all_day': e.all_day,
                        "summary": e.name,
                        "location": e.location,
                        "description": e.description if e.description is not None else "No description",
                        "canceled": e.status == "CANCELLED",

                    }
                )
            source.last_synced = start
            source.save()
