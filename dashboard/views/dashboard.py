from dataclasses import dataclass, asdict
from typing import List, Tuple, Dict, Literal
from datetime import datetime, timedelta
from dashboard.services.machine_stats import MachineStats, disk_usage_snapshot, DiskStat
from dashboard.services.docker_health import ContainerHealth, get_container_health
from dashboard.services.get_weather import wind_ms_to_beaufort, get_direction_letter_from_wind_dir, get_icon_from_code
from django.shortcuts import render
from django.views import View
from django.utils import timezone
from django.db.models import Prefetch
from dashboard.services.util import convert_unix_dt_to_datetime, local_date, bytes_to_size_notation
from dashboard.models.weather import DayForecast, Location, WeatherDetail
from dashboard.models.application import MinuteSystemSample
from dashboard.models.calendar import CalendarOccurrence, CalendarSource


@dataclass
class DashboardAlert:
    level: Literal["info", "warning", "error"]
    message: str


@dataclass
class DashboardHeaderView:
    hostname: str
    generated_at: datetime
    alerts: List[DashboardAlert]

@dataclass
class WeatherDetailView:
    icon: str
    main: str
    description: str

@dataclass
class WeatherDayView:
    label: str # "Wednesday" or "Today"
    # temps
    temp_day: str
    temp_min: str
    temp_max: str
    temp_night: str
    temp_eve: str
    temp_morn: str

    # feels_like
    feels_day: str
    feels_night: str
    feels_eve: str
    feels_morn: str
    wind_speed_bft: str
    wind_dir_letters: str
    wind_gust_bft: str | None
    wind_descr: str

    # Other
    cloud_pct: str
    uvi: str
    percipitation_probability_pct: str
    detail: WeatherDetailView

@dataclass
class DashboardWeatherView:
    days: List[WeatherDayView]
    updated_at: datetime


@dataclass
class DashboardMetricView:
    start_time: datetime
    end_time: datetime
    machinestats: MachineStats
    updated_at: datetime


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
class DashboardDockerHealthView:
    updated_at: datetime
    total_memory_used: str
    containers: List[ContainerHealth]


@dataclass
class DashboardStatsView:
    memory: DashboardStatView
    cpu: DashboardStatView
    network: DashboardStatView

@dataclass
class CalendarOccurrenceView:
    source: str
    title: str
    start: datetime
    end: datetime | None
    all_day: bool
    canceled: bool
    description: str | None
    location: str | None

@dataclass
class DashboardCalendarView:
    updated_at: datetime
    today: List[CalendarOccurrenceView]
    rest: List[CalendarOccurrenceView]


@dataclass
class DashboardViewData:
    header: DashboardHeaderView | None # None is not rendered
    weather: DashboardWeatherView | None
    disks: DashboardDisksView | None 
    stats: DashboardStatsView | None
    docker: DashboardDockerHealthView | None
    calendar: DashboardCalendarView | None

class DashboardView(View):

    def get_header(self,now: datetime) -> DashboardHeaderView:
        return DashboardHeaderView(
            hostname="Raspberry pi", # TODO: Change
            alerts=[],
            generated_at=now,
        )
    
    def get_calendar(self, now: datetime) -> DashboardCalendarView:
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        days_future = start_of_day + timedelta(days=60)
        items = CalendarOccurrence.objects.filter(
            instance_start__gte=start_of_day,
            instance_end__lt=days_future,
        ).select_related("source").order_by("instance_start")

        def make_view(item: CalendarOccurrence) -> CalendarOccurrenceView:
            return CalendarOccurrenceView(
                source=item.source.name,
                title=item.summary,
                start=item.instance_start,
                end=item.instance_end,
                all_day=item.all_day,
                description=item.description,
                location=item.location,
                canceled=item.canceled
            )
        
        item_views: List[CalendarOccurrenceView] = [make_view(item) for item in items]
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        today_bin = [v for v in item_views if start_of_day <= v.start < end_of_day]
        later_bin = [v for v in item_views if v.start >= end_of_day]

        return DashboardCalendarView(
            updated_at=now,
            today=today_bin,
            rest=later_bin
        )

    def get_weather(self, now: datetime) -> DashboardWeatherView:
        dates = [local_date(now + timedelta(days=i)) for i in range(6)]
        location = Location.objects.get(name="Blankenberge")
        qs = (
            DayForecast.objects
            .filter(location=location, date__in=set(dates))  # set() dedupes
            .order_by("date")                                # or "date","generated_at"
            .prefetch_related(
                Prefetch("weather_details", queryset=WeatherDetail.objects.all().order_by("id"))
            )
        )

        def make_view(forecast: DayForecast) -> WeatherDayView:
            detail: WeatherDetail = forecast.weather_details.all()[0] # type: ignore
            return WeatherDayView(
                label=forecast.date.strftime("%A"),
                temp_day=f"{forecast.temp_day:.1f}",
                temp_min=f"{forecast.temp_min:.1f}",
                temp_max=f"{forecast.temp_max:.1f}",
                temp_night=f"{forecast.temp_night:.1f}",
                temp_eve=f"{forecast.temp_eve:.1f}",
                temp_morn=f"{forecast.temp_morn:.1f}",

                # feels_like
                feels_day=f"{forecast.feels_day:.1f}",
                feels_night=f"{forecast.feels_night:.1f}",
                feels_eve=f"{forecast.feels_eve:.1f}",
                feels_morn=f"{forecast.feels_morn:.1f}",
                wind_speed_bft=str(wind_ms_to_beaufort(forecast.wind_speed)[0]),
                wind_dir_letters=get_direction_letter_from_wind_dir(forecast.wind_deg),
                wind_gust_bft=str(wind_ms_to_beaufort(forecast.wind_gust)[0] if forecast.wind_gust is not None else None),
                wind_descr=wind_ms_to_beaufort(forecast.wind_speed)[1],

                # Other
                cloud_pct=str(forecast.clouds),
                uvi=str(forecast.uvi),
                percipitation_probability_pct=str(int(forecast.precipitation_probability * 100.0)),
                detail=WeatherDetailView(
                    main=detail.main_type,
                    description=detail.description.capitalize(),
                    icon=get_icon_from_code(detail.weather_id) if detail.weather_id else ""
                )
            )
        
        days: List[WeatherDayView] = [ make_view(forecast) for forecast in qs]
        return DashboardWeatherView(
            updated_at=now,
            days=days,
        )
    
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
                        color="yellow"
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
    
    def get_docker(self, now)-> DashboardDockerHealthView:
        containers = get_container_health()
        total_memory_used = sum(container.mem_usage for container in containers)

        return DashboardDockerHealthView(
            updated_at=now,
            total_memory_used=bytes_to_size_notation(total_memory_used),
            containers=containers, # Value from service already view suitable
        )
    
    def get(self, request):
        now_minute = timezone.now().replace(second=0, microsecond=0)
        # Get alerts; for now empty list
        view_data = DashboardViewData(
            header = self.get_header(now_minute),
            stats=self.get_stats(now_minute),
            # docker=self.get_docker(now_minute),
            docker=None,
            weather=self.get_weather(now_minute),
            disks=self.get_disks(now_minute),
            calendar=self.get_calendar(now_minute)
        )
        return render(request, "dashboard/dashboard.html", context=asdict(view_data))
