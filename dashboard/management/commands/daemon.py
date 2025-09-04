import asyncio, json, socket, time
from datetime import timedelta
from django.core.management.base import BaseCommand
from dashboard.daemon.jobs import job_execution_task
from dashboard.daemon.display_discovery import udp_discovery_server_task
from dashboard.daemon.stats import stats_collector_task

class Command(BaseCommand):
    help = "Runs UDP discovery + minute scheduler(s) in one process"

    def handle(self, *args, **opts):
        async def main():
            tasks = [
                asyncio.create_task(udp_discovery_server_task(), name="udp"),
                asyncio.create_task(stats_collector_task(), name="stats"),
                asyncio.create_task(job_execution_task(), name="jobs"),
            ]
            loop = asyncio.get_running_loop()
            stop = asyncio.Event()
            for sig in ("SIGINT", "SIGTERM"):
                try:
                    import signal
                    loop.add_signal_handler(getattr(signal, sig), stop.set)
                except NotImplementedError:
                    pass  # e.g., on Windows

            await stop.wait()
            for t in tasks:
                t.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)

        asyncio.run(main())
