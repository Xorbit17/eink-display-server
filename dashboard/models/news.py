# app/models.py
from django.db import models

class CalendarSource(models.Model):
    name = models.CharField(max_length=120)
    ics_url = models.URLField()
    timezone = models.CharField(max_length=64, default="Europe/Brussels")
    active = models.BooleanField(default=True)

    # Optional fetch hints (some providers send these)
    etag = models.CharField(max_length=200, blank=True)
    last_modified = models.CharField(max_length=200, blank=True)

    last_synced = models.DateTimeField(null=True, blank=True)

    def __str__(self): return self.name


class CalendarOccurrence(models.Model):
    """
    One row per concrete event instance (recurrences are expanded).
    Store UTC in DB; convert to local in views.
    """
    source = models.ForeignKey(CalendarSource, on_delete=models.CASCADE, related_name="occurrences")
    uid = models.CharField(max_length=255)                      # VEVENT UID
    instance_start = models.DateTimeField(db_index=True)        # UTC
    instance_end = models.DateTimeField(null=True, blank=True)  # UTC
    all_day = models.BooleanField(default=False)

    summary = models.CharField(max_length=500, blank=True)
    location = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    canceled = models.BooleanField(default=False)               # STATUS:CANCELLED

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("source", "uid", "instance_start")]
        indexes = [
            models.Index(fields=["source", "instance_start"]),
            models.Index(fields=["instance_start"]),
        ]

    def __str__(self): return f"{self.summary} @ {self.instance_start}"
