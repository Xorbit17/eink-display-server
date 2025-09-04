from zoneinfo import ZoneInfo
from typing import Literal, Dict, List, Tuple, TypeAlias
from pathlib import Path

def parse_env_file(path: str | Path) -> Dict[str, str]:
    env: Dict[str, str] = {}
    path = Path(path)

    with path.open("r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip()
            if (value.startswith('"') and value.endswith('"')) or (
                value.startswith("'") and value.endswith("'")
            ):
                value = value[1:-1]
            env[key] = value
    return env


LOCAL_TZ = ZoneInfo("Europe/Brussels")
APP_DIR = Path(__file__).resolve().parents[0]  # app; a.k.a. the current django app
PROJECT_DIR = APP_DIR.parents[0]  # server; a.k.a the django root
PI_DIR = PROJECT_DIR.parents[
    0
]  # pi_home; a.k.a root of all sources of projects running on this pi
ENV_PATH = PI_DIR / ".env.server"
SECRETS = parse_env_file(ENV_PATH)

IMAGE_DIR = Path(SECRETS["IMAGE_DIR"])
ICAL_GOOGLE_CALENDAR_URL = SECRETS["ICAL_GOOGLE_CALENDAR_URL"]
OPENAI_KEY = SECRETS["OPENAI_KEY"]
OPENWEATHERMAP_KEY = SECRETS["OPENWEATHERMAP_KEY"]
OPENAI_PORTRAIT_SIZE= "1024x1536"
OPENAI_SQUARE_SIZE= "1024x1024"
OPENAI_LANDSCAPE_SIZE= "1536x1024"
IMAGE_ART_GENERATION_MODEL="gpt-5"

NEWS_MODE = "news"
PHOTO_MODE = "photo"
DASHBOARD_MODE = "dashboard"

MODE_CHOICES = [
    (NEWS_MODE, "Newspaper"),
    (PHOTO_MODE, "Photo"),
    (DASHBOARD_MODE, 'Dashboard')
]

ModeKind: TypeAlias = Literal[
    "NEWS_MODE",
    "PHOTO_MODE",
    "DASHBOARD_MODE"
]

WEEKDAY_CHOICES = [
    (0, "Mon"),
    (1, "Tue"),
    (2, "Wed"),
    (3, "Thu"),
    (4, "Fri"),
    (5, "Sat"),
    (6, "Sun"),
]

NEWS_KIND = "news"
PHOTO_KIND = "photo"

ASSET_CHOICES = [(NEWS_KIND, "Newspaper"), (PHOTO_KIND, "Photo")]

DEBUG = "DEBUG"
INFO = "INFO"
WARN = "WARN"
ERROR = "ERROR"

LOG_LEVEL_CHOICES = [
    (DEBUG, "Debug"),
    (INFO, "Info"),
    (WARN, "Warning"),
    (ERROR, "Error"),
]

CALENDAR = "CALENDAR"
RSS = "RSS"
WEATHER = "WEATHER"
PUSH = "PUSH"
ART = "ART"
NEWSPAPER = "NEWSPAPER"
CLASSIFY = "CLASSIFY"
MANUAL_TRIGGER = "MANUAL_TRIGGER"
DASHBOARD = "DASHBOARD"
DUMMY = "DUMMY"

JOB_KIND_CHOICES = [
    (CALENDAR, "Get calendar"),
    (RSS, "Get RSS"),
    (WEATHER, "Get weather"),
    (PUSH, "Push to displays"),
    (ART, "Generate art"),
    (NEWSPAPER, "Generate newspaper"),
    (CLASSIFY, "Classify image"),
    (MANUAL_TRIGGER, "Manually triggered"),
    (DASHBOARD, "Generate dashboard"),
    (DUMMY, "Dummy job to test the scheduler and the commands")
]

JobKind: TypeAlias = Literal[
    "CALENDAR",
    "RSS",
    "WEATHER",
    "PUSH",
    "ART",
    "NEWSPAPER",
    "CLASSIFY",
    "MANUAL_TRIGGER",
    "DUMMY",
    "DASHBOARD",
]

RUNNING = "RUNNING"
SUCCESS = "SUCCESS"
SKIPPED = "SKIPPED"
ERROR = "ERROR"
QUEUED = "QUEUED"

JOB_STATUS_CHOICES = [
    (RUNNING, "Running"),
    (SUCCESS, "Success"),
    (SKIPPED, "Skipped"),
    (ERROR, "Error"),
    (QUEUED, "Queued"),
]

JobStatus = Literal["RUNNING", "SUCCESS", "SKIPPED", "ERROR", "QUEUED"]

CRON = "CRON"
MANUAL = "MANUAL"

JOB_TYPE_CHOICES = [
    (CRON, "Triggered by chron"),
    (MANUAL, "Triggered manually"),
]

JobType = Literal["CRON", "MANUAL"]

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".heic"}
MIME_BY_EXT = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
    ".heic": "image/heic",
}
