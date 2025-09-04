from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from dashboard.models.job import Job 
from dashboard.models.weather import Location
from dashboard.models.calendar import CalendarSource
from dashboard.constants import CRON, CLASSIFY, ART, DUMMY, WEATHER
from dashboard.constants import LOCAL_TZ, ICAL_GOOGLE_CALENDAR_URL


class Command(BaseCommand):
    help = "Seed initial data: periodic jobs, etc."

    @transaction.atomic
    def handle(self, *args, **options):
        """
        Creates or updates a minimal set of cron-based jobs.
        Runs safely multiple times (idempotent).
        """
        seed_jobs = [
            {
                "name": "classify-new-images",
                "kind": CLASSIFY,   
                "job_type": CRON,
                "cron": "*/5 * * * *",  # every 5 minutes
                "enabled": True,
                "params": {},           # add API keys or tuning knobs later if needed
            },
            {
                "name": "generate-art-variants",
                "kind": ART,
                "job_type": CRON,
                "cron": "0 0 * * *",    # every day at midnight
                "enabled": True,
                "params": {},
            },
            {
                "name": "get_weather",
                "kind": WEATHER,
                "job_type": CRON,
                "cron": "55 5 * * *",    # every day at 05:45. Dashboard weather needs to be ready at 06:00
                "enabled": True,
                "params": {},
            },
            {
                "name": "dummy-heartbeat",
                "kind": DUMMY,
                "job_type": CRON,
                "cron": "* * * * *",    # every minute
                "enabled": True,
                "params": {},
            },
        ]

        seed_locations= [
            {
                "name": "Blankenberge",
                "country": "BE",
                "latitude": "51°18'15.5\"N",
                "longitude": "3°08'44.0\"E",
            }
        ]

        seed_calendar_sources = [
            {
                "name": "Default calendar",
                "ics_url": ICAL_GOOGLE_CALENDAR_URL,
                "timezone": LOCAL_TZ,
            }
        ]

        created, updated = 0, 0

        for spec in seed_jobs:
            obj, was_created = Job.objects.update_or_create(
                name=spec["name"],
                defaults={
                    "kind": spec["kind"],
                    "job_type": spec["job_type"],
                    "cron": spec["cron"],
                    "enabled": spec["enabled"],
                    "params": spec["params"],
                },
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created job: {obj.name}"))
            else:
                updated += 1
                self.stdout.write(self.style.WARNING(f"Updated job: {obj.name}"))

        for spec in seed_locations:
            obj, was_created = Location.objects.update_or_create(
                name=spec["name"],
                country=spec["country"],
                defaults={
                    "latitude": spec["latitude"],
                    "longitude": spec["longitude"]
                },

            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created Location: {obj.name}"))
            else:
                updated += 1
                self.stdout.write(self.style.WARNING(f"Updated Location: {obj.name}"))


        for cal in seed_calendar_sources:
            obj, was_created = CalendarSource.objects.update_or_create(
                ics_url=cal["ics_url"],
                defaults={
                     "name": cal["name"],
                     "timezone": cal["timezone"]
                },
            )
             
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created CalendarSource: {obj.name}"))
            else:
                updated += 1
                self.stdout.write(self.style.WARNING(f"Updated CalendarSource: {obj.name}"))

        

        self.stdout.write(self.style.SUCCESS(f"Seeding complete. Created: {created}, Updated: {updated}"))
