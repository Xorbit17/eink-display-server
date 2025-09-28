from dashboard.services.machine_stats import disk_usage_snapshot, DiskStat
from dashboard.services.util import bytes_to_size_notation
from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class DiskStatView:
    id: str
    disk_name: str
    disk_used_percent: float
    disk_unused_percent: float
    used: str
    total: str


@dataclass
class DashboardDisksView:
    updated_at: datetime
    disks: List[DiskStatView]

class DashboardDisksMixin:
    def get_disks(self, now: datetime) -> DashboardDisksView:
        disk_info = disk_usage_snapshot()

        def make_view(snap:DiskStat) -> DiskStatView:
            used_frac = snap.used / snap.total
            unused_frac = 1.0 - used_frac
            return DiskStatView(
                id=snap.device.replace("/","-"),
                disk_name=snap.device.replace("/dev/",""),
                disk_used_percent=used_frac * 100.0,
                disk_unused_percent=unused_frac * 100.0,
                used=bytes_to_size_notation(snap.used),
                total=bytes_to_size_notation(snap.total),
            )
        return DashboardDisksView(
            updated_at=now,
            disks=[make_view(snap) for snap in disk_info]
        )