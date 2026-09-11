import os
import sys
from pathlib import Path

# Paths
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    base_meipass = Path(sys._MEIPASS)
    if (base_meipass / "mousam_win" / "assets").exists():
        BASE_DIR = base_meipass / "mousam_win"
    elif (base_meipass / "assets").exists():
        BASE_DIR = base_meipass
    else:
        BASE_DIR = base_meipass
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

ASSETS_DIR = BASE_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
DEFAULT_ICONS_DIR = ICONS_DIR / "default_icons"
MATERIAL_ICONS_DIR = ICONS_DIR / "material_icons"

# API Endpoints
OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODING_BASE_URL = "https://geocoding-api.open-meteo.com/v1/search"
AIR_QUALITY_BASE_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

TIMEOUT = 12

# WMO Weather code to text mapping
WMO_CODE_TEXT = {
    0: "晴朗",
    1: "多云 (较少)",
    2: "多云 (局部)",
    3: "阴天",
    45: "大雾",
    48: "薄雾 / 沉积雾",
    51: "轻度毛毛雨",
    53: "中度毛毛雨",
    55: "强毛毛雨",
    56: "轻度冻雨",
    57: "强冻雨",
    61: "小雨",
    63: "中雨",
    65: "大雨",
    66: "轻微冻雨",
    67: "强冻雨",
    71: "小雪",
    73: "中雪",
    75: "大雪",
    77: "雪粒",
    80: "小阵雨",
    81: "中度阵雨",
    82: "暴烈阵雨",
    85: "小阵雪",
    86: "强阵雪",
    95: "雷暴",
    96: "雷暴伴随小冰雹",
    99: "强雷暴伴随大冰雹",
}

# Weather code to icon file name mapping
WMO_CODE_ICON = {
    "0": "clear-day.svg",
    "1": "overcast-day.svg",
    "2": "partly-cloudy-day.svg",
    "3": "overcast.svg",
    "45": "fog.svg",
    "48": "fog.svg",
    "51": "partly-cloudy-day-drizzle.svg",
    "53": "drizzle.svg",
    "55": "overcast-drizzle.svg",
    "56": "partly-cloudy-day-snow.svg",
    "57": "overcast-snow.svg",
    "61": "partly-cloudy-day-rain.svg",
    "63": "rain.svg",
    "65": "thunderstorms-rain.svg",
    "66": "overcast-snow.svg",
    "67": "thunderstorms-rain.svg",
    "71": "partly-cloudy-day-snow.svg",
    "73": "snow.svg",
    "75": "snowflake.svg",
    "77": "snowflake.svg",
    "80": "overcast-day-rain.svg",
    "81": "rain.svg",
    "82": "thunderstorms-rain.svg",
    "85": "snow.svg",
    "86": "snowflake.svg",
    "95": "thunderstorms-rain.svg",
    "96": "thunderstorms-day-overcast-snow.svg",
    "99": "snowflake.svg",

    # Night variants
    "0n": "clear-night.svg",
    "1n": "overcast-night.svg",
    "2n": "partly-cloudy-night.svg",
    "3n": "overcast.svg",
    "45n": "fog-night.svg",
    "48n": "fog-night.svg",
    "51n": "partly-cloudy-night-drizzle.svg",
    "53n": "drizzle.svg",
    "55n": "overcast-drizzle.svg",
    "56n": "partly-cloudy-night-snow.svg",
    "57n": "overcast-snow.svg",
    "61n": "partly-cloudy-night-rain.svg",
    "63n": "rain.svg",
    "65n": "thunderstorms-rain.svg",
    "66n": "overcast-snow.svg",
    "67n": "thunderstorms-rain.svg",
    "71n": "partly-cloudy-night-snow.svg",
    "73n": "snow.svg",
    "75n": "snowflake.svg",
    "77n": "snowflake.svg",
    "80n": "overcast-night-rain.svg",
    "81n": "rain.svg",
    "82n": "thunderstorms-rain.svg",
    "85n": "snow.svg",
    "86n": "snowflake.svg",
    "95n": "thunderstorms-night-rain.svg",
    "96n": "thunderstorms-night-overcast-snow.svg",
    "99n": "snowflake.svg",
}

def get_aqi_level(aqi: int) -> tuple[str, str]:
    """Returns (Level Text, Hex Color)"""
    if aqi <= 50:
        return ("优", "#10B981")
    elif aqi <= 100:
        return ("良", "#3B82F6")
    elif aqi <= 150:
        return ("轻度污染", "#F59E0B")
    elif aqi <= 200:
        return ("中度污染", "#F97316")
    elif aqi <= 300:
        return ("重度污染", "#EF4444")
    else:
        return ("严重污染", "#7C3AED")

def get_uv_level(uv: float) -> tuple[str, str]:
    """Returns (UV description, Hex Color)"""
    if uv <= 2:
        return ("低", "#10B981")
    elif uv <= 5:
        return ("中等", "#F59E0B")
    elif uv <= 7:
        return ("较高", "#F97316")
    elif uv <= 10:
        return ("极高", "#EF4444")
    else:
        return ("危险", "#7C3AED")
