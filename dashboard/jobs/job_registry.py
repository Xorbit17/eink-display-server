from __future__ import annotations
from importlib import import_module
import pkgutil
from typing import Dict, Any, Tuple, Type, Protocol
from dashboard.constants import JobStatus, JobType
from dashboard.models.job import Job, Execution
from django.utils import timezone
from typing import Optional, cast
from django.db import transaction
from pydantic import BaseModel

from dashboard.services.logger_job import JobLogger
class JobFunctionNotFoundException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class BadJobArgumentsException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class JobErrorException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class JobFunction(Protocol):
    def __call__(
        self,
        job: Job,
        logger: JobLogger,
        /,
        *args: Any,
        **kwargs: Any,
    ) -> None: ...


_registry: Dict[str, Tuple[JobFunction, Optional[Type[BaseModel]]]] = {}
_LOADED = False

def job_function(name: str, param_model: Optional[Type[BaseModel]] = None):
    def deco(fn: JobFunction) -> JobFunction:
        def job_function(
            job: Job, logger: JobLogger, /, *args: Any, **kwargs: Any
        ) -> None:
            if param_model:
                # Check
                validated_kwargs = param_model.model_validate(dict(**kwargs)).model_dump()
                result = fn(job, logger, *args, **validated_kwargs)
                return result
            return fn(job, logger, *args, **kwargs)

        _registry[name] = (job_function, param_model)
        return job_function

    return deco

def _iter_submodules(package: str):
    pkg = import_module(package)
    for modinfo in pkgutil.iter_modules(pkg.__path__, package + "."):
        yield modinfo.name
        
def load_all(package: str = "dashboard.jobs") -> None:
    global _LOADED
    if _LOADED:
        return
    for fullname in _iter_submodules(package):
        import_module(fullname)  # importing triggers decorators
    _LOADED = True

# Public API
def get_job_function_and_model(name: str) -> Tuple[JobFunction, Type[BaseModel] | None]:
    load_all()
    result = _registry.get(name, None)
    if not result:
        available = ", ".join(sorted(_registry))
        raise JobFunctionNotFoundException(
            f"No pipeline function '{name}'. Available: [{available}]"
        )
    return result

def get_job_function(name:str) -> JobFunction:
    load_all()
    return get_job_function_and_model(name)[0]
    
def test_job_sync(name: str, /, rethrow: bool = False, **kwargs):
    load_all()
    job = Job.objects.create(
        name="Manually triggered",
        job_function_name=name,
        job_type = JobType.MANUAL,
        enabled=True,
        params="",
    )
    execution = Execution.objects.create(
        job=job,
        started_at=timezone.now(),
        status=JobStatus.RUNNING,
        params=kwargs,
    )
    logger = JobLogger(job, execution)
    job_function = get_job_function_and_model(name)[0]
    try:
        job_function(job, logger, **kwargs)
        logger._close_success("Job execution succeeded")
    except Exception as e:
        logger._close_error(e, "Job execution failed")
        if rethrow:
            raise
    return logger

@transaction.atomic
def run_execution(execution: Execution):
    load_all()
    if not execution.status == JobStatus.RUNNING:
        raise RuntimeError(f"Execution with id {execution.pk} does not have status set to running")
    
    job = cast(Job, execution.job)
    Execution.objects.filter(pk=execution.pk, status=JobStatus.RUNNING).update(started_at=timezone.now())
    execution.refresh_from_db(fields=["status", "started_at"])

    logger = JobLogger(job, execution)
    job_function = get_job_function_and_model(job.job_function_name)[0]
    params = job.params
    try:
        job_function(job, logger, **params)
        logger._close_success("Job execution succeeded")
    except Exception as e:
        logger._close_error(e, "Job execution failed")
    return logger
