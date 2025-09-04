from django.core.management.base import BaseCommand, CommandError
from dashboard.constants import JOB_KIND_CHOICES, JobKind, RUNNING
from dashboard.jobs.job_registry import test_job

import dashboard.jobs.classify
import dashboard.jobs.dummy_job
import dashboard.jobs.generate_variant
import dashboard.jobs.get_weather
import dashboard.jobs.calendar
import dashboard.jobs.generate_dashboard

from typing import cast, Dict, Any
import json

VALID_CHOICES =  [t[0] for t in JOB_KIND_CHOICES]

class Command(BaseCommand):
    help = "Runs a specific job. First arg is the job kind; named args are job-specific."

    def add_arguments(self, parser):
        # positional: restrict to known kinds
        parser.add_argument("job_kind", choices=VALID_CHOICES)

        # repeatable key=value flags, e.g. --param source_image_id=1
        parser.add_argument(
            "--param",
            action="append",
            default=[],
            metavar="KEY=VALUE",
            help="Job parameter (repeatable). Example: --param source_image_id=1",
        )

        # OR provide a JSON dict in one go
        parser.add_argument(
            "--params-json",
            type=str,
            default=None,
            help='JSON dict of parameters. Example: --params-json \'{"source_image_id":1}\'',
        )

    def handle(self, *args, **options):
        job_kind = options["job_kind"]
        params: Dict[str, Any] = {}
        if options.get("params_json"):
            try:
                params.update(json.loads(options["params_json"]))
            except json.JSONDecodeError as e:
                raise CommandError(f"--params-json is not valid JSON: {e}")

        # Merge KEY=VALUE pairs (override JSON if the same key appears)
        for item in options.get("param", []):
            if "=" not in item:
                raise CommandError(f"--param must be KEY=VALUE (got: {item!r})")
            key, value = item.split("=", 1)
            params[key] = value

        test_job(cast(JobKind, job_kind), params=params)
