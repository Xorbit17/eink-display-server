from dashboard.jobs.job_registry import job_function
from dashboard.services.logger_job import JobLogger
from pydantic import BaseModel, PositiveInt
from typing import Optional
from time import sleep
class DummyJobParams(BaseModel):
    wait_time_ms: Optional[PositiveInt] = 0
    message: Optional[str] = "No message"


@job_function("dummy", DummyJobParams)
def dummy_job(_, logger: JobLogger, wait_time_ms, message):
    to_print = "Starting dummy job" if not message else message
    logger.info(to_print)
    if wait_time_ms:
        sleep(wait_time_ms / 1000.0)
