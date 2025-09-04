from __future__ import annotations

from django.db import models
from django.utils import timezone
from dashboard.constants import (
    LogLevel,
    JobKind,
    JobStatus,
    JobType,
)


class Job(models.Model):
    name = models.CharField(max_length=120)
    kind = models.CharField(max_length=64, choices=JobKind.choices())
    job_type = models.CharField(max_length=64, choices=JobType.choices())
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
        choices=JobStatus.choices(),
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

    status = models.CharField(max_length=20, choices=JobStatus.choices())
    summary = models.CharField(max_length=500, blank=True, default="")
    error = models.TextField(blank=True, default="")  # full traceback if any

    params = models.JSONField(null=True, default=None)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        when = self.started_at.isoformat() if self.started_at else "pending"
        return f"Execution({self.pk}): job={self.job} status={self.status} @ {when}"


ACTIVE_STATUSES = [JobStatus.RUNNING, JobStatus.QUEUED]


class JobLogEntry(models.Model):
    execution = models.ForeignKey(
        Execution,
        on_delete=models.CASCADE,
        related_name="logs",
    )
    ts = models.DateTimeField(default=timezone.now, db_index=True)
    level = models.CharField(
        max_length=10,
        choices=LogLevel.choices(),
        default=LogLevel.INFO,
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