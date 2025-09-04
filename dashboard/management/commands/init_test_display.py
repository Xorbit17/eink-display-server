from django.core.management.base import BaseCommand, CommandError
from dashboard.services.display import create_new_display
import uuid


class Command(BaseCommand):
    help = "Runs a specific job. First arg is the job kind; named args are job-specific."

    def handle(self, *args, **options):
        create_new_display("127.0.0.1",f"test-display-{uuid.uuid4()}",1200,1600)
        