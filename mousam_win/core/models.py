from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Location:
    name: str
    country: str = ""
    state: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    timezone: str = "auto"

    @property
    def display_name(self) -> str:
        parts = [self.name]
        if self.state and self.state != self.name:
            parts.append(self.state)
        if self.country:
            parts.append(self.country)
        return ", ".join(parts)

@dataclass
class CurrentWeather:
    time: str
    temperature: float
    feels_like: float
    humidity: int
    pressure: float
    wind_speed: float
    wind_direction: int
    uv_index: float
    weather_code: int
    is_day: int
    precipitation: float
    condition_text: str = ""
    icon_name: str = ""

@dataclass
class HourlyItem:
    time_str: str          # e.g., "14:00"
    timestamp: int
    temperature: float
    weather_code: int
    precip_prob: int       # %
    wind_speed: float
    is_day: int
    icon_name: str = ""

@dataclass
class DailyItem:
    date_str: str          # e.g., "2026-09-11"
    weekday: str           # e.g., "今天", "周六"
    temp_max: float
    temp_min: float
    weather_code: int
    precip_prob_max: int
    sunrise_str: str
    sunset_str: str
    uv_max: float
    condition_text: str = ""
    icon_name: str = ""

@dataclass
class AirQuality:
    aqi: int
    pm2_5: float
    pm10: float
    no2: float
    o3: float
    so2: float
    co: float
    level_text: str = ""
    level_color: str = ""

@dataclass
class FullWeatherData:
    location: Location
    current: CurrentWeather
    hourly: List[HourlyItem] = field(default_factory=list)
    daily: List[DailyItem] = field(default_factory=list)
    air_quality: Optional[AirQuality] = None
