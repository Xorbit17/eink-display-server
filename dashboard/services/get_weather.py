import re
import requests

from dashboard.constants import OPENWEATHERMAP_KEY
import datetime as python_datetime
from django.utils.timezone import make_aware
from typing import List, Optional, Iterable, Tuple
from pydantic import BaseModel, ValidationError


class WeatherItem(BaseModel):
    id: int
    main: str
    description: str
    icon: str

class CurrentModel(BaseModel):
    dt: int
    sunrise: int
    sunset: int
    temp: float
    feels_like: float
    pressure: int
    humidity: int
    dew_point: float
    uvi: float
    clouds: int # %
    visibility: int
    wind_speed: float
    wind_deg: int
    wind_gust: float
    weather: List[WeatherItem]


class TempModel(BaseModel):
    day: float
    min: float
    max: float
    night: float
    eve: float
    morn: float


class FeelsLikeModel(BaseModel):
    day: float
    night: float
    eve: float
    morn: float


class DailyItem(BaseModel):
    dt: int
    sunrise: int
    sunset: int
    moonrise: int
    moonset: int
    moon_phase: float
    summary: Optional[str] = ""  # 'summary' isn't always present in official responses
    temp: TempModel
    feels_like: FeelsLikeModel
    pressure: int
    humidity: int
    dew_point: float
    wind_speed: float
    wind_deg: int
    wind_gust: float
    weather: List[WeatherItem]
    clouds: int
    pop: float  # Probability of precipitation (0–100)
    rain: Optional[float] = None
    snow: Optional[float] = None
    uvi: float


class OneCallResponse(BaseModel):
    lat: float
    lon: float
    timezone: str
    timezone_offset: int
    current: CurrentModel
    daily: List[DailyItem]



def dms_to_decimal(dms_str):
    """
    Converts a DMS string (e.g. 51°18'15.5\"N) to decimal degrees as float.
    """
    pattern = re.compile(
        r"""(?P<degrees>\d+)[°\s]+(?P<minutes>\d+)[\'\s]+(?P<seconds>\d+(?:\.\d+)?)[\"\s]*(?P<direction>[NSEW])""",
        re.VERBOSE,
    )

    match = pattern.match(dms_str.strip())
    if not match:
        raise ValueError(f"Invalid DMS coordinate: {dms_str}")

    deg = float(match.group("degrees"))
    minutes = float(match.group("minutes"))
    sec = float(match.group("seconds"))
    direction = match.group("direction")

    decimal = deg + minutes / 60 + sec / 3600
    if direction in ("S", "W"):
        decimal = -decimal

    return decimal


def convert_lat_lon(lat_str, lon_str):
    """
    Returns a tuple (latitude, longitude) in decimal degrees
    from DMS strings.
    """
    return dms_to_decimal(lat_str), dms_to_decimal(lon_str)


class OpenWeatherError(RuntimeError):
    pass

def fetch_weather(
    lat: float,
    lon: float,
    api_key: str,
    exclude: Optional[Iterable[str]] = None,
    units: str = "metric",
    lang: str = "en",
    timeout: float = 10.0,
) -> OneCallResponse:
    url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": units,
        "lang": lang,
    }

    if exclude:
        excl = {"hourly", *map(str.strip, exclude)}
        params["exclude"] = ",".join(sorted(excl))

    try:
        resp = requests.get(url, params=params, timeout=timeout)
    except requests.RequestException as e:
        raise OpenWeatherError(f"Network error talking to OpenWeather: {e}") from e

    if resp.status_code == 401:
        raise OpenWeatherError("Unauthorized (401): check your API key.")
    if resp.status_code == 429:
        raise OpenWeatherError("Rate limited (429): too many requests.")
    # TODO: raise for other 4xx/5xx?
    resp.raise_for_status()
    json = resp.json()

    try:
        return OneCallResponse.model_validate(json)
    except ValidationError as ve:
        raise OpenWeatherError(f"Response validation failed: {ve}") from ve

def get_weather(location: Tuple[str,str]):
    lat,lon = convert_lat_lon(*location)
    api_key = OPENWEATHERMAP_KEY
    return fetch_weather(lat,lon,api_key)

OWM_CODE_TO_ICON = {
    # Thunderstorm (2xx)
    200: "thunderstorms-rain.svg",
    201: "thunderstorms-rain.svg",
    202: "thunderstorms-extreme-rain.svg",
    210: "thunderstorms.svg",
    211: "thunderstorms.svg",
    212: "thunderstorms-extreme.svg",
    221: "thunderstorms.svg",
    230: "thunderstorms-rain.svg",
    231: "thunderstorms-rain.svg",
    232: "thunderstorms-extreme-rain.svg",

    # Drizzle (3xx)
    300: "drizzle.svg",
    301: "drizzle.svg",
    302: "drizzle.svg",
    310: "drizzle.svg",
    311: "drizzle.svg",
    312: "drizzle.svg",
    313: "drizzle.svg",
    314: "drizzle.svg",
    321: "drizzle.svg",

    # Rain (5xx)
    500: "partly-cloudy-day-rain.svg",
    501: "partly-cloudy-day-rain.svg",
    502: "rain.svg",
    503: "rain.svg",
    504: "extreme-rain.svg",
    511: "sleet.svg",              # freezing rain
    520: "rain.svg",
    521: "rain.svg",
    522: "extreme-rain.svg",
    531: "rain.svg",

    # Snow (6xx)
    600: "snow.svg",
    601: "snow.svg",
    602: "extreme-snow.svg",
    611: "sleet.svg",
    612: "sleet.svg",
    613: "sleet.svg",
    615: "sleet.svg",
    616: "sleet.svg",
    620: "snow.svg",
    621: "snow.svg",
    622: "extreme-snow.svg",

    # Atmosphere (7xx)
    701: "mist.svg",
    711: "smoke.svg",
    721: "haze.svg",
    731: "dust.svg",               # sand/dust whirls
    741: "fog.svg",
    751: "dust.svg",               # sand
    761: "dust.svg",               # dust
    762: "extreme.svg",            # volcanic ash (generic extreme icon)
    771: "wind.svg",               # squalls
    781: "tornado.svg",

    # Clear (800)
    800: "clear-day.svg",

    # Clouds (80x)
    801: "partly-cloudy-day.svg",
    802: "partly-cloudy-day.svg",
    803: "overcast-day.svg",
    804: "overcast.svg",
}


def get_icon_from_code(code:int) -> str:
    result = OWM_CODE_TO_ICON.get(code, None)
    if not result:
        raise Exception(f"Corresponding icon not mapped for open weather code '{code}'")
    return result

dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
def get_direction_letter_from_wind_dir(dir: float) -> str:
    deg = dir % 360
    idx = int((deg + 22.5) // 45) % 8
    return dirs[idx]

bft_scale = [
    (0.3, 0, "Calm"),
    (1.6, 1, "Light air"),
    (3.4, 2, "Light breeze"),
    (5.5, 3, "Gentle breeze"),
    (8.0, 4, "Moderate breeze"),
    (10.8, 5, "Fresh breeze"),
    (13.9, 6, "Strong breeze"),
    (17.2, 7, "Near gale"),
    (20.8, 8, "Gale"),
    (24.5, 9, "Strong gale"),
    (28.5, 10, "Storm"),
    (32.7, 11, "Violent storm"),
]

def wind_ms_to_beaufort(speed: float) -> tuple[int, str]:
    """
    Convert wind speed (m/s) into the Beaufort scale (0–12) and description.
    Returns (scale, description).
    """

    for limit, num, desc in bft_scale:
        if speed < limit:
            return num, desc
    return 12, "Hurricane force"






    


    

