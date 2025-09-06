import os
from typing import Dict
from pathlib import Path
from enum import Enum, IntEnum

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



APP_DIR = Path(__file__).resolve().parents[0]  # app; a.k.a. the current django app 'dashboard'
PROJECT_DIR = APP_DIR.parents[0]  # server; a.k.a the django root
OPENAI_PORTRAIT_SIZE= "1024x1536"
OPENAI_SQUARE_SIZE= "1024x1024"
OPENAI_LANDSCAPE_SIZE= "1536x1024"
IN_DOCKER = os.environ["IN_DOCKER"].lower() == "true" or os.environ["IN_DOCKER"] == "1"
class LabeledEnum(str, Enum):
    """
    An enum that has a label for each member, and can generate
    a list of (value, label) pairs for use in Django choices.
    """
    label: str

    def __new__(cls, value, label):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj

    @classmethod
    def choices(cls):
        return [(key.value, key.label) for key in cls]

class Mode(LabeledEnum):
    NEWS = ("news", "Newspaper")
    PHOTO = ("photo", "Photo")
    DASHBOARD = ("dashboard", "Dashboard")

class Weekday(IntEnum):
    MON = 0
    TUE = 1
    WED = 2
    THU = 3
    FRI = 4
    SAT = 5
    SUN = 6

    @classmethod
    def choices(cls):
        # Returns a list of (value, label) pairs for use in Django choices.
        # e.g. [(0, 'Mon'), (1, 'Tue'), ...]
        return [(day.value, day.name.title()) for day in cls]


class AssetKind(LabeledEnum):
    NEWS = ("news", "Newspaper")
    PHOTO = ("photo", "Photo")

class LogLevel(LabeledEnum):
    DEBUG = ("DEBUG", "Debug")
    INFO = ("INFO", "Info")
    WARN = ("WARN", "Warning")
    ERROR = ("ERROR", "Error")

class JobStatus(LabeledEnum):
    RUNNING = ("RUNNING", "Running")
    SUCCESS = ("SUCCESS", "Success")
    SKIPPED = ("SKIPPED", "Skipped")
    ERROR = ("ERROR", "Error")
    QUEUED = ("QUEUED", "Queued")

class JobType(LabeledEnum):
    CRON = ("CRON", "Triggered by chron")
    MANUAL = ("MANUAL", "Triggered manually")

# NOTE: The previous TypeAlias definitions for Pydantic have been removed.
# Pydantic models can use these Enums directly for validation.

class QualityClassification(LabeledEnum):
    NOT_SUITED = ("NOT_SUITED", "Not suited")
    BAD = ("BAD", "Bad")
    PASSABLE = ("PASSABLE", "Passable")
    GOOD = ("GOOD", "Good")
    VERY_GOOD = ("VERY_GOOD", "Very good")
class RenderDecision(LabeledEnum):
    BOTH = ("BOTH", "Both")
    ARTIFY = ("ARTIFY", "Artify")
    LEAVE_PHOTO = ("LEAVE_PHOTO", "Leave photo")

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".heic"}
MIME_BY_EXT = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
    ".heic": "image/heic",
}
