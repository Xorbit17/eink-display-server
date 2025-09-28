from dashboard.models.calendar import CalendarOccurrence
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List


@dataclass
class CalendarOccurrenceView:
    source: str
    title: str
    start: datetime
    end: datetime | None
    all_day: bool
    canceled: bool
    description: str | None
    location: str | None


@dataclass
class DashboardCalendarView:
    updated_at: datetime
    today: List[CalendarOccurrenceView]
    rest: List[CalendarOccurrenceView]


class CalendarMixin:
    def get_calendar(self, now: datetime) -> DashboardCalendarView:
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        days_future = start_of_day + timedelta(days=60)
        items = (
            CalendarOccurrence.objects.filter(
                instance_start__gte=start_of_day,
                instance_end__lt=days_future,
            )
            .select_related("source")
            .order_by("instance_start")
        )

        def make_view(item: CalendarOccurrence) -> CalendarOccurrenceView:
            return CalendarOccurrenceView(
                source=item.source.name,
                title=item.summary,
                start=item.instance_start,
                end=item.instance_end,
                all_day=item.all_day,
                description=item.description,
                location=item.location,
                canceled=item.canceled,
            )

        item_views: List[CalendarOccurrenceView] = [make_view(item) for item in items]
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        today_bin = [v for v in item_views if start_of_day <= v.start < end_of_day]
        later_bin = [v for v in item_views if v.start >= end_of_day]

        return DashboardCalendarView(updated_at=now, today=today_bin, rest=later_bin)
