from dashboard.models.application import MinuteSystemSample
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List

@dataclass
class GraphStatView:
    id: str
    color: str
    labels: List[int]
    values: List[float | None]

@dataclass
class DashboardStatView:
    updated_at: datetime
    stat_id_and_grid: str
    stat_icon_path: str
    stat_title: str
    graph_data: List[GraphStatView]

@dataclass
class DashboardStatsView:
    memory: DashboardStatView
    cpu: DashboardStatView
    network: DashboardStatView

class DashboardStatsMixin:
    def get_stats(self, now: datetime) -> DashboardStatsView:
        one_hour_ago = now - timedelta(hours=1)
        qs = MinuteSystemSample.objects.filter(
            minute__gte=one_hour_ago,
            minute__lte=now
        ).order_by("minute")

        result = DashboardStatsView(
            memory = DashboardStatView(
                updated_at=now,
                stat_id_and_grid="memory",
                stat_icon_path="device-sd-card.svg",
                stat_title="Memory usage and swap (GB)",
                graph_data=[
                    GraphStatView(
                        id="memory-ram-graph",
                        labels = [],
                        values = [],
                        color="blue"
                    ),
                    GraphStatView(
                        id="memory-swap-graph",
                        labels = [],
                        values = [],
                        color="red"
                    )
                ],
            ),
            cpu = DashboardStatView(
                updated_at=now,
                stat_id_and_grid="cpu",
                stat_icon_path="cpu.svg",
                stat_title="CPU usage (% of total)",
                graph_data=[GraphStatView(
                    id="cpu-graph",
                    labels = [],
                    values = [],
                    color="green"
                )],
            ),
            network=DashboardStatView(
                updated_at=now,
                stat_id_and_grid="network",
                stat_icon_path="network.svg",
                stat_title="Network download and upload (Mbps)",
                graph_data=[
                    GraphStatView(
                        id="network--down-graph",
                        labels = [],
                        values = [],
                        color="purple"
                    ),
                    GraphStatView(
                        id="memory-up-graph",
                        labels = [],
                        values = [],
                        color="darkYellow"
                    ),
                ],
            ),
        )

        def minutes_diff(ts) -> int:
            delta = ts - now
            return int(delta.total_seconds() // 60)
        # TODO optimise? A lot of list memory reallocaton. Decimate?
        for sample in qs:
            diff_label = minutes_diff(sample.minute)
            result.memory.graph_data[0].labels.append(diff_label)
            result.memory.graph_data[1].labels.append(diff_label)
            result.memory.graph_data[0].values.append(float(sample.mem_used_avg))
            result.memory.graph_data[1].values.append(float(sample.swap_used_avg) if sample.swap_used_avg else None)

            result.cpu.graph_data[0].labels.append(diff_label)
            result.cpu.graph_data[0].values.append(sample.cpu_percent_avg)

            result.network.graph_data[0].labels.append(diff_label)
            result.network.graph_data[1].labels.append(diff_label)
            result.network.graph_data[0].values.append(float(sample.rx_bps_avg / 1000000) if sample.rx_bps_avg else None)
            result.network.graph_data[1].values.append(float(sample.tx_bps_avg / 1000000) if sample.tx_bps_avg else None)

        return result


