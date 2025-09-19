from dashboard.image_processing_pipeline.pipeline_registry import load_pipeline, process
from dashboard.jobs.job_registry import job_function
from dashboard.services.logger_job import JobLogger
from pydantic import BaseModel
from typing import Optional
import json
from pathlib import Path

class RunTestPipeLine(BaseModel):
    input: str
    pipeline_json_file: str
    output: Optional[str] = None


@job_function("run_test_pipeline", RunTestPipeLine)
def run_test_pipeline(_, logger: JobLogger, input: str, pipeline_json_file, output):
    with open(pipeline_json_file,'r') as f:
        serialised = json.load(f)
    pipeline = load_pipeline(serialised)
    input_path = Path(input)
    if output:
        output_path = Path(output)
    else:
        output_path = input_path.resolve().parent / "test-output.png"
    process(
        input_path,
        pipeline,
        output_path=output_path,
        logger=logger,
    )
    logger.info("Pipeline processing function finished.")