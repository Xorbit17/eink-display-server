from __future__ import annotations
import asyncio
import time
from datetime import datetime, timedelta
from django.utils import timezone

async def sleep_until_monotonic(target_mono: float) -> None:
    """
    Sleep until the given monotonic deadline. Wakes ~50ms early in small steps
    to reduce overshoot jitter.
    """
    loop = asyncio.get_running_loop()
    while True:
        now = loop.time()  # event loop's monotonic clock
        dt = target_mono - now
        if dt <= 0:
            return
        await asyncio.sleep(min(dt, 0.05))

def next_minute_start(now: datetime | None = None) -> datetime:
    """
    Return the next minute boundary in wall-clock time.
    If called exactly on a boundary, returns that boundary.
    """
    now = now or timezone.now()
    floor = now.replace(second=0, microsecond=0)
    return floor if now == floor else floor + timedelta(minutes=1)

async def sleep_until_next_minute() -> datetime:
    """
    Sleep until the next wall-clock minute boundary using a monotonic deadline.
    Returns the *actual* minute boundary at wake (recomputed), so it is correct
    even if NTP/DST adjusted the wall clock during the sleep.
    """
    loop = asyncio.get_running_loop()

    wall_now = timezone.now()
    target_wall = next_minute_start(wall_now)

    wait_s = (target_wall - wall_now).total_seconds()
    target_mono = loop.time() + max(0.0, wait_s)

    await sleep_until_monotonic(target_mono)
    return next_minute_start(timezone.now().replace(second=0, microsecond=0))
