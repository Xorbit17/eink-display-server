from __future__ import annotations

from django.db import models
from django.utils import timezone
from dashboard.constants import (
    LOG_LEVEL_CHOICES,
    JOB_KIND_CHOICES,
    JOB_STATUS_CHOICES,
    JOB_TYPE_CHOICES,
    QUEUED,
    RUNNING,
)


class Job(models.Model):
    name = models.CharField(max_length=120)
    kind = models.CharField(max_length=64, choices=JOB_KIND_CHOICES)
    job_type = models.CharField(max_length=64, choices=JOB_TYPE_CHOICES)
    cron = models.CharField(
        max_length=64, help_text="Cron format, e.g. '0 5 * * *'", null=True
    )
    enabled = models.BooleanField(default=True)

    # Optional parameters for the handler
    params = models.JSONField(default=dict, blank=True)

    # Health / observability
    last_run_started_at = models.DateTimeField(null=True, blank=True)
    last_run_finished_at = models.DateTimeField(null=True, blank=True)
    last_run_status = models.CharField(
        null=True,
        max_length=64,
        choices=JOB_STATUS_CHOICES,
    )
    last_run_message = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Job({self.pk}): {self.name} [{self.kind}]"


class Execution(models.Model):
    job = models.ForeignKey("Job", on_delete=models.CASCADE, related_name="executions")

    started_at = models.DateTimeField(null=True, default=None)
    finished_at = models.DateTimeField(null=True, default=None)
    runtime_ms = models.PositiveIntegerField(null=True, default=None)

    status = models.CharField(max_length=20, choices=JOB_STATUS_CHOICES)
    summary = models.CharField(max_length=500, blank=True, default="")
    error = models.TextField(blank=True, default="")  # full traceback if any

    params = models.JSONField(null=True, default=None)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        when = self.started_at.isoformat() if self.started_at else "pending"
        return f"Execution({self.pk}): job={self.job} status={self.status} @ {when}"


ACTIVE_STATUSES = [RUNNING, QUEUED]


class JobLogEntry(models.Model):
    execution = models.ForeignKey(
        Execution,
        on_delete=models.CASCADE,
        related_name="logs",
    )
    ts = models.DateTimeField(default=timezone.now, db_index=True)
    level = models.CharField(
        max_length=10,
        choices=LOG_LEVEL_CHOICES,
        default="INFO",
        db_index=True,
    )
    message = models.TextField()
    context = models.JSONField(null=True, default=None)
    # A monotonic counter to preserve order without depending on timestamps
    seq = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return (
            f"JobLogEntry({self.pk}): exec:{self.execution} #{self.seq} [{self.level}]"
        )

