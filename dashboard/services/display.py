from dashboard.models.schedule import Display, WeeklyRule
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
import secrets
import string
import re
from django.conf import settings
from django.utils import timezone
from datetime import time
from dashboard.constants import PHOTO_MODE, DASHBOARD_MODE
from django.db import transaction
from typing import Tuple

TIME_ZONE = getattr(settings, "TIME_ZONE")

READABLE_LOWER = ''.join(ch for ch in string.ascii_lowercase if ch not in "ilo")

ID_REGEX = re.compile(r"^[a-z]{3}-[a-z]{3}-[a-z]{3}$")

def generate_display_id(groups: int = 3, group_len: int = 3, alphabet: str = READABLE_LOWER) -> str:
    """
    Generate an easy-to-read ID like 'abc-def-ghi'.
    - default total length: 9 (3 groups of 3)
    - lowercase only
    """
    return "-".join(
        "".join(secrets.choice(alphabet) for _ in range(group_len))
        for _ in range(groups)
    )

def is_valid_display_id(s: str) -> bool:
    return bool(ID_REGEX.fullmatch(s))

def get_display_by_hardware_id(hardware_id: str):
    return Display.objects.get(hardware_id=hardware_id)

MIDNIGHT=time(0,0,0)
BREAKFAST=time(6,0,0)
MORNING=time(9,0,0)
NOON=time(12,0,0)
AFTERNOON=time(14,0,0)


def create_default_schedule(display: Display) -> None:
    with transaction.atomic():
        for i in range(7):
            WeeklyRule.objects.create(
                display=display,
                weekday=i, # Monday is 0, tuesday is 1 etc
                start_time=MIDNIGHT,
                end_time=BREAKFAST,
                mode=PHOTO_MODE,
            )
            WeeklyRule.objects.create(
                display=display,
                weekday=i,
                start_time=BREAKFAST,
                end_time=MORNING,
                mode=DASHBOARD_MODE,
            )
            WeeklyRule.objects.create(
                display=display,
                weekday=i,
                start_time=MORNING,
                end_time=NOON,
                mode=PHOTO_MODE,
            )
            WeeklyRule.objects.create(
                display=display,
                weekday=i,
                start_time=NOON,
                end_time=AFTERNOON,
                mode=DASHBOARD_MODE,
            )
            WeeklyRule.objects.create(
                display=display,
                weekday=i,
                start_time=AFTERNOON,
                end_time=MIDNIGHT,
                mode=PHOTO_MODE,
            )


def create_new_display(
        host, 
        hardware_id: str, 
        x_res, 
        y_res,
        tz_name=TIME_ZONE,
        generate_default_schedule=True,
    ) -> Tuple[Display,User,str]:
    human_readable_id = generate_display_id()

    user = User.objects.create_user(
        username=f"disp-{human_readable_id}", password=None, is_active=True
    )
    display = Display.objects.create(
        user=user,
        host=host,
        hardware_id=hardware_id,
        human_readable_id=human_readable_id,
        timezone=tz_name,
        last_seen=timezone.now(),
        x_res=x_res,
        y_res=y_res,
    )
    token = Token.objects.create(user=user)
    if generate_default_schedule:
        create_default_schedule(display)

    return display, user, token.key
    