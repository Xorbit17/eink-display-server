from typing import Callable, Dict, Any, Tuple, Type
from dashboard.constants import JobKind, RUNNING, QUEUED, MANUAL, CRON
from dashboard.models.job import Job, Execution
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from datetime import datetime
from typing import Optional, Dict, cast
from django.db import transaction
from pydantic import BaseModel

from dashboard.services.logger_job import RunLogger

Handler = Callable[[Job, RunLogger, Any], str | None]

_registry: Dict[str, Tuple[Handler, Optional[Type[BaseModel]]]] = {}

def register(kind: JobKind, param_model: Optional[Type[BaseModel]] = None):
    def deco(fn: Handler):
        _registry[kind] = (fn, param_model)
        return fn
    return deco

def get_handler(kind: JobKind) -> Handler:
    try:
        return _registry[kind][0]
    except KeyError:
        raise KeyError(f"No handler registered for kind '{kind}'")
    
def get_validator(kind: JobKind) -> Type[BaseModel] | None:
    try:
        return _registry[kind][1]
    except KeyError:
        raise KeyError(f"No validator registered for kind '{kind}'. Shoud be defined and automatically None if no params. Impossible")
    
def test_job(jobKind: JobKind, rethrow: bool = False, *, params: Dict[str,Any]):
    validator = get_validator(jobKind)
    validated_params = None
    if validator:
        validated_params = validator.model_validate(params)
    job = Job.objects.create(
        name="Manually triggered",
        kind=jobKind,
        job_type = MANUAL,
        enabled=True,
        params="",
    )
    execution = Execution.objects.create(
        job=job,
        started_at=timezone.now(),
        status=RUNNING,
        params=params or {},
    )
    logger = RunLogger(job, execution)
    handler = get_handler(jobKind)
    try:
        handler(job, logger, validated_params)
        logger._close_success("Job execution succeeded")
    except Exception as e:
        logger._close_error(e, "Job execution failed")
        if rethrow:
            raise
    return logger

@transaction.atomic
def run_execution(execution: Execution):
    if not execution.status == RUNNING:
        raise RuntimeError(f"Execution with id {execution.pk} does not have status set to running")
    
    job = cast(Job, execution.job)
    Execution.objects.filter(pk=execution.pk, status=RUNNING).update(started_at=timezone.now())
    execution.refresh_from_db(fields=["status", "started_at"])

    logger = RunLogger(job, execution)
    handler = get_handler(cast(JobKind,job.kind))
    validator = get_validator(cast(JobKind,job.kind))
    params  = validator.model_validate(execution.params) if validator else {}
    try:
        handler(job, logger, params)
        logger._close_success("Job execution succeeded")
    except Exception as e:
        logger._close_error(e, "Job execution failed")
    return logger
