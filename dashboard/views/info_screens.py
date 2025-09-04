from dataclasses import dataclass, asdict
from typing import List, Tuple, Dict, Literal
from datetime import datetime
from dashboard.services.machine_stats import MachineStats, disk_usage_snapshot, DiskStat
from dashboard.services.docker_health import ContainerHealth, get_container_health
from dashboard.services.get_weather import wind_ms_to_beaufort, get_direction_letter_from_wind_dir, get_icon_from_code
from django.shortcuts import render
from django.views import View
from django.utils import timezone
from django.db.models import Prefetch
from django.http import JsonResponse, FileResponse
from django.core.exceptions import ObjectDoesNotExist
from dashboard.services.util import convert_unix_dt_to_datetime, local_date, bytes_to_size_notation
from dashboard.models.schedule import Display
from pydantic import BaseModel, ValidationError
import socket
import psutil

def querydict_to_data(qd):
    data = {}
    for key, values in qd.lists():
        if len(values) == 1:
            data[key] = values[0]
        else:
            data[key] = values
    return data

def get_all_lan_ips():
    ips = []
    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                ip = addr.address
                # exclude loopback
                if not ip.startswith("127."):
                    ips.append(ip)
    return ips



@dataclass
class KeyValue:
    key: str
    value: str

@dataclass
class BootScreenData:
    updated_at: datetime
    bootinfo: List[KeyValue]
    # TODO add schedule view

class BootstrapRequestURLQueryParams(BaseModel):
    pk: int
    

class BootScreenView(View):
    def get(self, request):
        raw = querydict_to_data(request.GET)
        try:
            params = BootstrapRequestURLQueryParams.model_validate(raw)
        except ValidationError as e:
            # 400 Bad Request with structured errors
            return JsonResponse(
                {"detail": "Invalid query parameters", "errors": e.errors()},
                status=400,
            )
        try:
            display = Display.objects.get(pk=params.pk)
        except ObjectDoesNotExist as e:
            return JsonResponse(
                {"detail": f"Display with primary key {params.pk} not found", "error": str(e)},
                status=404,
            )

        view_data = BootScreenData(
            updated_at=timezone.localtime(),
            bootinfo=[
                KeyValue("Hostname", display.host),
                KeyValue("Horizontal resolution", str(display.x_res) + " px"),
                KeyValue("Vertical resolution", str(display.y_res) + " px"),
                KeyValue("Hardware ID", display.hardware_id),
                KeyValue("Human readable ID", display.human_readable_id),
                KeyValue("Default mode", display.default_mode),
                KeyValue("Display server hostname", socket.gethostname()),
                KeyValue("Display server LAN IP's", ",".join(get_all_lan_ips())),
            ]
        )

        return render(request, "dashboard/bootstrap.html", context=asdict(view_data))