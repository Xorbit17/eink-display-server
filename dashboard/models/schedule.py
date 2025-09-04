# app/models/schedule.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Optional, cast

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from zoneinfo import ZoneInfo
from dashboard.constants import MODE_CHOICES, NEWS_MODE, PHOTO_MODE, WEEKDAY_CHOICES, ModeKind
from django.contrib.auth.models import User

MIDNIGHT = time(0,0,0)

def _minutes_since_midnight(t: time) -> int:
    return t.hour * 60 + t.minute

def _end_minutes(end_t: time) -> int:
    # Edge case. If end_t is midnight and we are looing for the end time this means
    # the end of the day, not the beginning
    mins = _minutes_since_midnight(end_t)
    return 24 * 60 if mins == 0 else mins

@dataclass
class _Window:
    start_min: int
    end_min: int
    mode: ModeKind

class Display(models.Model):
    """
    A physical e-ink frame (or logical display).
    You can have multiple with independent schedules.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="display")
    host = models.CharField(
        max_length=255,
        help_text="How the server reaches the device, e.g. 'http://hallway-pi:8080' or 'http://192.168.1.52:8080'",
    )
    hardware_id = models.CharField(max_length=255, unique=True) # Example "6a:6b:9b:a1:cb:38"
    human_readable_id= models.CharField(max_length=16, unique=True)
    timezone = models.CharField(max_length=64, default="Europe/Brussels")
    default_mode = models.CharField(max_length=16, choices=MODE_CHOICES, default=PHOTO_MODE)
    override_mode = models.CharField(max_length=16, choices=MODE_CHOICES, null=True, default=None)
    last_seen = models.DateTimeField(null=True) # NULL means display has never connected
    x_res = models.PositiveIntegerField()
    y_res = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Display"
        verbose_name_plural = "Displays"

    def __str__(self) -> str:
        return f"Display with username:'{self.user.username}', and hardware id: '{self.human_readable_id}'. ({self.x_res}x{self.y_res})"

    @property
    def tz(self) -> ZoneInfo:
        return ZoneInfo(self.timezone)

    def clear_expired_override(self, now: Optional[datetime] = None) -> None:
        now = (now or timezone.now())
        if self.override_mode and self.override_expires_at and now >= self.override_expires_at:
            self.override_mode = None
            self.override_expires_at = None
            self.save(update_fields=["override_mode", "override_expires_at"])

class WeeklyRule(models.Model):
    display = models.ForeignKey(Display, on_delete=models.CASCADE, related_name="weekly_rules")
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES)  # 0=Mon .. 6=Sun
    start_time = models.TimeField(help_text="Inclusive local start")
    end_time = models.TimeField(help_text="Exclusive local end; use 00:00 for 'until midnight'")
    mode = models.CharField(max_length=16, choices=MODE_CHOICES, default=PHOTO_MODE)
    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Weekly Rule"
        verbose_name_plural = "Weekly Rules"
        indexes = [
            models.Index(fields=["display", "weekday", "active"]),
        ]
        ordering = ["display", "weekday", "start_time"]
    
    def clean(self):
        if self.start_time == self.end_time:
            raise ValidationError("start_time and end_time cannot be equal.")

        
        start_min = _minutes_since_midnight(self.start_time)
        end_min = _end_minutes(self.end_time)

        qs = WeeklyRule.objects.filter(display=self.display, weekday=self.weekday, active=True)
        if self.pk:
            qs = qs.exclude(pk=self.pk)

        for other in qs:
            o_start = _minutes_since_midnight(other.start_time)
            o_end = _end_minutes(other.end_time)
            # intervals [start, end)
            overlap = not (end_min <= o_start or o_end <= start_min)
            if overlap:
                raise ValidationError(
                    f"Overlaps with rule: {other.start_time.strftime('%H:%M')}-"
                    f"{other.end_time.strftime('%H:%M') if other.end_time != time(0,0) else '24:00'}"
                )

    @staticmethod
    def _windows_for_day(display: Display, weekday: int) -> list[_Window]:
        rules = (WeeklyRule.objects
                 .filter(display=display, weekday=weekday, active=True)
                 .order_by("start_time"))
        windows: list[_Window] = []
        for r in rules:
            s = _minutes_since_midnight(r.start_time)
            e = _end_minutes(r.end_time)
            windows.append(_Window(start_min=s, end_min=e, mode=cast(ModeKind,r.mode)))
        return windows

    @staticmethod
    def resolve_mode(display: Display, now: Optional[datetime] = None) -> ModeKind:
        display.clear_expired_override()

        local_now = timezone.localtime() if now is None else timezone.make_aware(now)
        # In case of override
        if display.override_mode and display.override_expires_at:

            if now < display.override_expires_at:
                return cast(ModeKind,display.override_mode)
        # Normal case: schedule
        weekday = local_now.weekday()
        minutes = local_now.hour * 60 + local_now.minute

        windows = WeeklyRule._windows_for_day(display, weekday)
        for w in windows:
            if w.start_min <= minutes < w.end_min:
                return w.mode

        # If nothing matched (e.g., schedule gaps or no schedule), fall back to default
        return cast(ModeKind,display.default_mode)

    @staticmethod
    def next_boundary_for_display(display: Display, now_local: Optional[datetime] = None) -> Optional[datetime]:
        """
        Find the next *local* datetime when the schedule changes (next window start).
        Used to set override expiry conveniently.
        """
        if now_local is None:
            now_local = timezone.now().astimezone(display.tz)

        weekday = now_local.weekday()
        minutes = now_local.hour * 60 + now_local.minute
        
        def as_dt(day_offset: int, minute_mark: int) -> datetime:
            target_date = (now_local.date() + timedelta(days=day_offset))
            hh, mm = divmod(minute_mark, 60)
            return datetime(target_date.year, target_date.month, target_date.day, hh, mm, tzinfo=display.tz)

        todays = WeeklyRule._windows_for_day(display, weekday)
        for w in todays:
            if w.start_min > minutes:
                return as_dt(0, w.start_min)

        for step in range(1, 8):
            wd = (weekday + step) % 7
            wins = WeeklyRule._windows_for_day(display, wd)
            if wins:
                return as_dt(step, wins[0].start_min)

        return None  # no rules at all
