import datetime
from django.utils import timezone


def convert_unix_dt_to_datetime(unix):
    dt_naive = datetime.datetime.fromtimestamp(unix)
    return timezone.make_aware(dt_naive)

def local_date(dt):
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.utc)
    dt_local = timezone.localtime(dt)
    return dt_local.date()

def bytes_to_size_notation(nbytes: int) -> str:
    units = ["B", "kB", "MB", "GB", "TB", "PB"]
    size = float(nbytes)
    for unit in units:
        if size < 1000:
            return f"{size:.1f}{unit}".rstrip("0").rstrip(".")
        size /= 1000
    return f"{size:.1f}EB".rstrip("0").rstrip(".")  # in case it's *really* huge