from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
from django.db.models import Q
from dashboard.models.calendar import CalendarOccurrence
from dashboard.constants import LOCAL_TZ, ICAL_GOOGLE_CALENDAR_URL
from ics import Calendar, Event
import requests
from django.utils import timezone
import arrow
from typing import Iterable

def _day_bounds(dt_local):
    start = datetime.combine(dt_local.date(), time(0,0,0, tzinfo=LOCAL_TZ))
    end = start + timedelta(days=1)
    return start, end

def today_events():
    now = datetime.now(LOCAL_TZ)
    start_local, end_local = _day_bounds(now)
    start_utc = start_local.astimezone(ZoneInfo("UTC"))
    end_utc = end_local.astimezone(ZoneInfo("UTC"))
    qs = (CalendarOccurrence.objects
          .filter(instance_start__gte=start_utc,
                  instance_start__lt=end_utc,
                  canceled=False)
          .order_by("-all_day", "instance_start"))  # all-day first
    return list(qs)

def next_7_days():
    now = datetime.now(LOCAL_TZ)
    start_local, _ = _day_bounds(now)  # midnight today
    end_local = start_local + timedelta(days=7)
    start_utc = start_local.astimezone(ZoneInfo("UTC"))
    end_utc = end_local.astimezone(ZoneInfo("UTC"))
    qs = (CalendarOccurrence.objects
          .filter(instance_start__gte=start_utc,
                  instance_start__lt=end_utc,
                  canceled=False)
          .order_by("-all_day", "instance_start"))
    return list(qs)

def get_calendar(source_url: str, start: datetime, end: datetime | None = None) -> Iterable[Event]:
    if not timezone.is_aware(start) or ((end is not None) and not timezone.is_aware(end)):
        raise TypeError("Get calendar only takes time zone aware inputs.")
    text = requests.get(source_url).text
    c = Calendar(text)
    if end is None:
        return list(c.timeline.start_after(arrow.get(start)))
    result = [
        event 
        for event in c.timeline.start_after(arrow.get(start))
        if not event.end < arrow.get(end)
    ]
    return result
