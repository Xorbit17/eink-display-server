from dashboard.jobs.job_registry import register
from dashboard.services.logger_job import RunLogger
from pydantic import BaseModel, PositiveInt
from typing import Optional
from time import sleep

class DummyJobParams(BaseModel):
    wait_time_ms: Optional[PositiveInt] = 0
    message: Optional[str] = None


@register('DUMMY', DummyJobParams)
def dummy_job(_, logger: RunLogger, params: DummyJobParams):
    message = "Starting dummy job" if not params.message else f"Starting dummmy job: {params}"
    logger.info(message)
    if params.wait_time_ms:
        sleep(params.wait_time_ms / 1000.0)

