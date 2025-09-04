from dataclasses import dataclass, field
from typing import Optional, Dict, Any, cast
from django.utils import timezone
import traceback
from dashboard.models.job import Job, JobLogEntry, Execution
from dashboard.constants import RUNNING, QUEUED, SUCCESS, ERROR, JobKind

MAX_LINES_PER_RUN = 500

@dataclass
class RunLogger:
    job: Job
    execution: Execution
    _seq: int = 0
    _lines_written: int = 0
    _closed: bool = False
    _agg: Dict[str, int] = field(default_factory=dict)

    def _write(self, level: str, message: str, context: Optional[Dict[str, Any]] = None):
        if self._closed or self._lines_written >= MAX_LINES_PER_RUN:
            return
        self._seq += 1
        self._lines_written += 1
        safeContext = context
        # NOTE: either add a JSONField 'context' to JobLogEntry OR drop it here:
        JobLogEntry.objects.create(
            execution=self.execution,
            level=level,
            message=message,
            seq=self._seq,
            context=context
        )
        print(f"{level}:{message}")

    def debug(self, msg, **ctx): self._write("DEBUG", msg, ctx or None)
    def info(self, msg, **ctx):  self._write("INFO",  msg, ctx or None)
    def warn(self, msg, **ctx):  self._write("WARN",  msg, ctx or None)
    def error(self, msg, **ctx): self._write("ERROR", msg, ctx or None)

    def incr(self, key: str, by: int = 1):
        self._agg[key] = self._agg.get(key, 0) + by

    def _start(self):
        now = timezone.now()
        self.execution.status = RUNNING
        self.execution.started_at = now
        self.execution.save()

    def _close_success(self, summary: str = ""):
        if self._closed: return
        self._closed = True
        now = timezone.now()
        started = self.execution.started_at or now
        self.execution.summary = summary[:500]
        self.execution.status = SUCCESS
        self.execution.finished_at = now
        self.execution.runtime_ms = int((now - started).total_seconds() * 1000)
        self.execution.save()
        self.job.last_run_status = SUCCESS
        self.job.last_run_started_at = self.execution.started_at
        self.job.last_run_finished_at = self.execution.finished_at
        self.job.save()
        self.debug(f"Job Execution finished:\nSummary: {summary}")

    def _close_error(self, exc: BaseException, summary: str = ""):
        if self._closed: return
        self._closed = True
        now = timezone.now()
        tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        self.execution.summary = (summary or str(exc))[:500]
        self.execution.error = tb
        self.execution.status = ERROR
        self.execution.finished_at = now
        started = self.execution.started_at or now
        self.execution.runtime_ms = int((now - started).total_seconds() * 1000)
        self.execution.save()
        self.job.last_run_status = ERROR
        self.job.last_run_started_at = self.execution.started_at
        self.job.last_run_finished_at = self.execution.finished_at
        self.job.save()
        self.error(f"Job Execution error:\nSummary: {summary}\nTraceback: {tb}")