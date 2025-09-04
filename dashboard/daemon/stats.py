# stats.py
from __future__ import annotations
import asyncio
import psutil
from datetime import datetime
from django.db import close_old_connections
from django.utils import timezone

from .time_util import sleep_until_next_minute, sleep_until_monotonic
from dashboard.models.application import MinuteSystemSample

SAMPLES_PER_MIN = 60

def _avg(vals):
    return (sum(vals) / len(vals)) if vals else 0.0

async def collect(minute_start: datetime) -> dict:
    """Collect ~60 samples across the minute boundary."""
    cpu_vals = []
    mem_used_vals, mem_avail_vals = [], []
    swap_used_vals = []
    rx_bps_vals, tx_bps_vals = [], []

    mem_total = None
    swap_total = None

    loop = asyncio.get_running_loop()
    last_io = psutil.net_io_counters()
    last_mono = loop.time()
    target = loop.time()

    # Prime CPU window (non-blocking)
    psutil.cpu_percent(interval=None)

    for _ in range(SAMPLES_PER_MIN):
        # advance the next tick boundary by exactly 1.0s monotonic
        target += 1.0
        await sleep_until_monotonic(target)

        # CPU: % since previous call (≈ 1s window)
        cpu_vals.append(psutil.cpu_percent(interval=None))

        # Memory / Swap
        vm = psutil.virtual_memory()
        if mem_total is None:
            mem_total = int(vm.total)
        mem_used_vals.append(int(vm.used))
        mem_avail_vals.append(int(vm.available))

        sm = psutil.swap_memory()
        if swap_total is None:
            swap_total = int(sm.total) if sm.total else None
        if sm.total:
            swap_used_vals.append(int(sm.used))

        # Network B/s from monotonic-timed deltas
        now_mono = loop.time()
        io = psutil.net_io_counters()
        dt = max(1e-6, now_mono - last_mono)
        drx = io.bytes_recv - last_io.bytes_recv
        dtx = io.bytes_sent - last_io.bytes_sent
        if drx >= 0:
            rx_bps_vals.append(drx / dt)
        if dtx >= 0:
            tx_bps_vals.append(dtx / dt)
        last_io, last_mono = io, now_mono

    return {
        "minute": minute_start,
        "cpu_percent_avg": _avg(cpu_vals),
        "mem_total": mem_total or 0,
        "mem_used_avg": int(_avg(mem_used_vals)),
        "mem_available_avg": int(_avg(mem_avail_vals)),
        "swap_total": swap_total,
        "swap_used_avg": int(_avg(swap_used_vals)) if swap_used_vals else None,
        "rx_bps_avg": _avg(rx_bps_vals),
        "tx_bps_avg": _avg(tx_bps_vals),
    }

async def stats_collector_task():
    """
    Run once per minute, aligned to the wall clock.
    """
    while True:
        minute = await sleep_until_next_minute()
        try:
            stats = await collect(minute)  # ~60s of sampling with awaits (non-blocking to the loop)

            # Offload the single ORM write to a thread
            def write():
                close_old_connections()
                try:
                    MinuteSystemSample.objects.create(**stats)
                finally:
                    close_old_connections()

            await asyncio.to_thread(write)

        except Exception as e:
            # TODO: Deamon logger without a job (replace with your logger)
            print(f"[stats_collector] error: {e!r}")
