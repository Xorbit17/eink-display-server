
import psutil
from datetime import timedelta, datetime
from dashboard.models.application import MinuteSystemSample
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class DiskStat:
    device: str
    mount: str
    fstype: str
    total: int
    used: int
    free: int
    percent: float

def disk_usage_snapshot() -> List[DiskStat]:
    disks = []
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except PermissionError:
            continue
        disks.append(DiskStat(
            device=part.device,
            mount=part.mountpoint,
            fstype=part.fstype,
            total=usage.total,
            used=usage.used,
            free=usage.free,
            percent=usage.percent,
        ))
    return disks

@dataclass
class MachineStats:
    times: List[datetime]
    cpu_percent_avg: List[float]
    mem_total: List[int]
    mem_used_avg: List[int]
    mem_available_avg: List[int]
    swap_total: List[Optional[int]]
    swap_used_avg: List[Optional[int]]
    rx_bps_avg: List[Optional[float]]
    tx_bps_avg: List[Optional[float]]

def get_machine_stats(from_time: datetime, to_time: Optional[datetime] = None) -> MachineStats:
    if to_time is None:
        to_time = from_time + timedelta(hours=1)

    qs = (MinuteSystemSample.objects
          .filter(minute__gte=from_time, minute__lt=to_time)
          .order_by("minute")
          .values(
              "minute",
              "cpu_percent_avg",
              "mem_total",
              "mem_used_avg",
              "mem_available_avg",
              "swap_total",
              "swap_used_avg",
              "rx_bps_avg",
              "tx_bps_avg",
          ))

    rows = list(qs)
    if not rows:
        return MachineStats([], [], [], [], [], [], [], [], [])

    times, cpu, mem_tot, mem_used, mem_avail, swap_tot, swap_used, rx_bps, tx_bps = zip(*(
        (
            r["minute"],
            r["cpu_percent_avg"],
            r["mem_total"],
            r["mem_used_avg"],
            r["mem_available_avg"],
            r["swap_total"],
            r["swap_used_avg"],
            r["rx_bps_avg"],
            r["tx_bps_avg"],
        )
        for r in rows
    ))

    return MachineStats(
        times=list(times),
        cpu_percent_avg=list(cpu),
        mem_total=list(mem_tot),
        mem_used_avg=list(mem_used),
        mem_available_avg=list(mem_avail),
        swap_total=list(swap_tot),
        swap_used_avg=list(swap_used),
        rx_bps_avg=list(rx_bps),
        tx_bps_avg=list(tx_bps),
    )

