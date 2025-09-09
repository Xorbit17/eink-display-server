from django.core.management.base import BaseCommand, CommandError
from dashboard.jobs import test_job_sync

from typing import cast, Dict, Any
import json

class Command(BaseCommand):
    help = "Runs a specific job. First arg is the job job_function_name; named args are job-specific."

    def add_arguments(self, parser):
        # positional: restrict to known kinds
        parser.add_argument("job_name")

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
            help='JSON dict of parameters. Example: --params-json \'{\"source_image_id\":1}\'',
        )

    def handle(self, *args, **options):
        job_name = options["job_name"]

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

        test_job_sync(job_name,**params)

    