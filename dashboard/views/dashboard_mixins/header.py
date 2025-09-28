from dataclasses import dataclass
from datetime import datetime
from typing import Literal, List

@dataclass
class DashboardAlert:
    level: Literal["info", "warning", "error"]
    message: str

@dataclass
class DashboardHeaderView:
    hostname: str
    generated_at: datetime
    alerts: List[DashboardAlert]

class DashboardHeaderMixin:
    def get_header(self,now: datetime) -> DashboardHeaderView:
        return DashboardHeaderView(
            hostname="Raspberry pi", # TODO: Change
            alerts=[],
            generated_at=now,
        )