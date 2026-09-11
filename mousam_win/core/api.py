import datetime
from datetime import datetime, timezone, timedelta
from typing import List, Optional
import requests

from .configs import (
    OPEN_METEO_BASE_URL,
    AIR_QUALITY_BASE_URL,
    GEOCODING_BASE_URL,
    TIMEOUT,
    WMO_CODE_TEXT,
    get_aqi_level,
    get_uv_level,
)
from .models import (
    Location,
    CurrentWeather,
    HourlyItem,
    DailyItem,
    AirQuality,
    FullWeatherData,
)

WEEKDAY_ZH = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

def fetch_full_weather(location: Location, unit: str = "metric") -> FullWeatherData:
    """
    Fetch current, hourly, and daily forecasts, plus air quality.
    """
    temp_unit = "fahrenheit" if unit == "imperial" else "celsius"
    wind_unit = "mph" if unit == "imperial" else "kmh"
    precip_unit = "inch" if unit == "imperial" else "mm"

    # 1. Main Weather API
    weather_params = {
        "latitude": location.latitude,
        "longitude": location.longitude,
        "current": (
            "temperature_2m,relative_humidity_2m,apparent_temperature,is_day,"
            "precipitation,weather_code,surface_pressure,wind_speed_10m,wind_direction_10m"
        ),
        "hourly": (
            "temperature_2m,relative_humidity_2m,dew_point_2m,apparent_temperature,"
            "precipitation_probability,precipitation,weather_code,surface_pressure,"
            "visibility,wind_speed_10m,wind_direction_10m,uv_index,is_day"
        ),
        "daily": (
            "weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset,"
            "precipitation_probability_max,uv_index_max"
        ),
        "temperature_unit": temp_unit,
        "wind_speed_unit": wind_unit,
        "precipitation_unit": precip_unit,
        "timezone": "auto",
        "timeformat": "unixtime",
        "forecast_days": 10,
    }

    resp = requests.get(OPEN_METEO_BASE_URL, params=weather_params, timeout=TIMEOUT)
    resp.raise_for_status()
    wdata = resp.json()

    # Parse Current
    curr = wdata.get("current", {})
    wcode = curr.get("weather_code", 0)
    is_day = curr.get("is_day", 1)
    
    current_weather = CurrentWeather(
        time=datetime.fromtimestamp(curr.get("time", 0)).strftime("%H:%M"),
        temperature=round(curr.get("temperature_2m", 0.0), 1),
        feels_like=round(curr.get("apparent_temperature", 0.0), 1),
        humidity=int(curr.get("relative_humidity_2m", 0)),
        pressure=round(curr.get("surface_pressure", 1013.25), 1),
        wind_speed=round(curr.get("wind_speed_10m", 0.0), 1),
        wind_direction=int(curr.get("wind_direction_10m", 0)),
        uv_index=0.0,
        weather_code=wcode,
        is_day=is_day,
        precipitation=curr.get("precipitation", 0.0),
        condition_text=WMO_CODE_TEXT.get(wcode, "多云"),
    )

    # Parse Hourly (All available, up to 10 days)
    hourly = wdata.get("hourly", {})
    times = hourly.get("time", [])
    temps = hourly.get("temperature_2m", [])
    codes = hourly.get("weather_code", [])
    probs = hourly.get("precipitation_probability", [])
    winds = hourly.get("wind_speed_10m", [])
    days = hourly.get("is_day", [])
    uvs = hourly.get("uv_index", [])

    current_ts = curr.get("time", 0)
    start_idx = 0
    for i, t in enumerate(times):
        if t >= current_ts - 1800:
            start_idx = i
            break

    hourly_list: List[HourlyItem] = []
    for i in range(len(times)):
        t_val = times[i]
        dt = datetime.fromtimestamp(t_val)
        time_display = "现在" if i == start_idx else dt.strftime("%H:%M")
        
        # Assign current UV if index matches
        if i == start_idx and uvs and i < len(uvs):
            current_weather.uv_index = round(uvs[i] or 0.0, 1)

        hourly_list.append(HourlyItem(
            time_str=time_display,
            timestamp=t_val,
            temperature=round(temps[i] if i < len(temps) else 0.0, 1),
            weather_code=codes[i] if i < len(codes) else 0,
            precip_prob=int(probs[i] if i < len(probs) and probs[i] is not None else 0),
            wind_speed=round(winds[i] if i < len(winds) else 0.0, 1),
            is_day=days[i] if i < len(days) else 1,
        ))

    # Parse Daily (10 days)
    daily = wdata.get("daily", {})
    d_times = daily.get("time", [])
    d_codes = daily.get("weather_code", [])
    d_maxs = daily.get("temperature_2m_max", [])
    d_mins = daily.get("temperature_2m_min", [])
    d_probs = daily.get("precipitation_probability_max", [])
    d_sunrises = daily.get("sunrise", [])
    d_sunsets = daily.get("sunset", [])
    d_uvs = daily.get("uv_index_max", [])

    daily_list: List[DailyItem] = []
    for i in range(min(10, len(d_times))):
        ts = d_times[i]
        dt = datetime.fromtimestamp(ts)
        weekday = "今天" if i == 0 else WEEKDAY_ZH[dt.weekday()]
        
        sr_str = datetime.fromtimestamp(d_sunrises[i]).strftime("%H:%M") if i < len(d_sunrises) else "--:--"
        ss_str = datetime.fromtimestamp(d_sunsets[i]).strftime("%H:%M") if i < len(d_sunsets) else "--:--"
        c = d_codes[i] if i < len(d_codes) else 0

        daily_list.append(DailyItem(
            date_str=dt.strftime("%m月%d日"),
            weekday=weekday,
            temp_max=round(d_maxs[i] if i < len(d_maxs) else 0.0, 1),
            temp_min=round(d_mins[i] if i < len(d_mins) else 0.0, 1),
            weather_code=c,
            precip_prob_max=int(d_probs[i] if i < len(d_probs) and d_probs[i] is not None else 0),
            sunrise_str=sr_str,
            sunset_str=ss_str,
            uv_max=round(d_uvs[i] if i < len(d_uvs) and d_uvs[i] is not None else 0.0, 1),
            condition_text=WMO_CODE_TEXT.get(c, "多云"),
        ))

    # 2. Air Quality API
    aq_data = None
    try:
        aq_params = {
            "latitude": location.latitude,
            "longitude": location.longitude,
            "current": "us_aqi,european_aqi,pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone",
            "timezone": "auto",
        }
        aq_resp = requests.get(AIR_QUALITY_BASE_URL, params=aq_params, timeout=TIMEOUT)
        if aq_resp.status_code == 200:
            aq_json = aq_resp.json().get("current", {})
            val_aqi = int(aq_json.get("us_aqi") or aq_json.get("european_aqi") or 0)
            lvl_text, lvl_col = get_aqi_level(val_aqi)
            aq_data = AirQuality(
                aqi=val_aqi,
                pm2_5=round(aq_json.get("pm2_5", 0.0), 1),
                pm10=round(aq_json.get("pm10", 0.0), 1),
                no2=round(aq_json.get("nitrogen_dioxide", 0.0), 1),
                o3=round(aq_json.get("ozone", 0.0), 1),
                so2=round(aq_json.get("sulphur_dioxide", 0.0), 1),
                co=round(aq_json.get("carbon_monoxide", 0.0), 1),
                level_text=lvl_text,
                level_color=lvl_col,
            )
    except Exception as e:
        print(f"Air quality fetch warning: {e}")

    return FullWeatherData(
        location=location,
        current=current_weather,
        hourly=hourly_list,
        daily=daily_list,
        air_quality=aq_data,
    )


def search_cities(query: str, count: int = 6) -> List[Location]:
    """Search cities using Open-Meteo Geocoding API."""
    if not query.strip():
        return []

    # First try Chinese language
    params = {
        "name": query.strip(),
        "count": count,
        "language": "zh",
        "format": "json"
    }

    try:
        resp = requests.get(GEOCODING_BASE_URL, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])
        
        # If no results in zh, fallback to en
        if not results:
            params["language"] = "en"
            resp = requests.get(GEOCODING_BASE_URL, params=params, timeout=TIMEOUT)
            if resp.status_code == 200:
                results = resp.json().get("results", [])

        cities: List[Location] = []
        for item in results:
            cities.append(Location(
                name=item.get("name", ""),
                country=item.get("country", ""),
                state=item.get("admin1", ""),
                latitude=item.get("latitude", 0.0),
                longitude=item.get("longitude", 0.0),
                timezone=item.get("timezone", "auto")
            ))
        return cities
    except Exception as e:
        print(f"Error searching cities: {e}")
        return []
