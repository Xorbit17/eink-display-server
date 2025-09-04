from datetime import timedelta, datetime
from dashboard.constants import RUNNING, QUEUED, CRON

from django.db import transaction, close_old_connections
from django.db.models import Exists, OuterRef, Q
from django.utils import timezone
from croniter import croniter

from dashboard.models.job import Job, Execution
from dashboard.jobs.job_registry import run_execution
from .time_util import sleep_until_next_minute, next_minute_start
from daemon import time_util
import asyncio

ACTIVE_STATUSES = [RUNNING, QUEUED]

def _cron_due_this_minute(expr: str, now: datetime) -> bool:
    """True if cron expr fires at 'now' (minute precision)."""
    base = now.replace(second=0, microsecond=0)
    prev = croniter(expr, base + timedelta(minutes=1)).get_prev(datetime)
    return prev == base

def find_eligible_jobs(now: datetime) -> list[Job]:
    base_minute = now.replace(second=0, microsecond=0)

    active_execs = Execution.objects.filter(
        job=OuterRef("pk"),
        status__in=ACTIVE_STATUSES,
    )

    qs = (
        Job.objects
        .filter(cron__isnull=False, enabled=True, job_type=CRON)
        .filter(Q(last_run_finished_at__isnull=True) | Q(last_run_finished_at__lt=base_minute))
        .annotate(active_exists=Exists(active_execs))
        .filter(active_exists=False)  # push to SQL
    )

    # Cron match done in Python (minute precision)
    return [j for j in qs if _cron_due_this_minute(j.cron or "", now)]

def queue_due_jobs(now: datetime):
    base_minute = now.replace(second=0, microsecond=0)
    due = find_eligible_jobs(now)
    if not due:
        return

    due_ids = [j.pk for j in due]

    with transaction.atomic():
        # Lock the Job rows we plan to touch to prevent duplicate enqueues
        (Job.objects
            .select_for_update()
            .filter(pk__in=due_ids)
            .order_by("pk")
            .exists())  # materialize the lock

        for job in Job.objects.in_bulk(due_ids).values():
            already_running = Execution.objects.filter(
                job=job, status__in=ACTIVE_STATUSES
            ).exists()
            finished_this_minute = (
                job.last_run_finished_at is not None
                and job.last_run_finished_at >= base_minute
            )
            if not already_running and not finished_this_minute:
                Execution.objects.create(
                    job=job,
                    status=QUEUED,
                    params=job.params or {},
                )


async def job_execution_task():
    while True:
        minute_start = await sleep_until_next_minute()

        def work():
            close_old_connections()
            try:
                queue_due_jobs(minute_start)

                # Single-runner policy: if anything is RUNNING, skip this minute
                if Execution.objects.filter(status=RUNNING).exists():
                    print("A job is still running; try again next minute.")
                    return

                # Claim queued jobs atomically
                with transaction.atomic():
                    qs = (
                        Execution.objects
                        .select_related("job")
                        .select_for_update(skip_locked=True)
                        .filter(status=QUEUED)
                        .order_by("created_at")
                    )
                    executions = list(qs)
                    # Mark RUNNING inside txn so others can't claim them
                    now = timezone.now()
                    for e in executions:
                        e.status = RUNNING
                        e.started_at = now
                        e.save(update_fields=["status", "started_at"])

                # Run outside the transaction, serially, in order
                for e in executions:
                    try:
                        run_execution(e)  # must set finished_at + status DONE/FAILED
                    except Exception as err:
                        # Defensive fallback if run_execution didn’t catch
                        Execution.objects.filter(pk=e.pk).update(
                            status="FAILED",
                            finished_at=timezone.now(),
                            error=str(err)[:1000],
                        )
            finally:
                close_old_connections()

        await asyncio.to_thread(work)

