import json
import os
from pathlib import Path
from typing import Dict, Any, List
from .models import Location

CONFIG_DIR = Path(os.getenv("APPDATA", str(Path.home()))) / "Mousam"
CONFIG_FILE = CONFIG_DIR / "settings.json"

DEFAULT_SETTINGS: Dict[str, Any] = {
    "selected_city": {
        "name": "北京",
        "country": "中国",
        "state": "北京市",
        "latitude": 39.9042,
        "longitude": 116.4074,
        "timezone": "Asia/Shanghai"
    },
    "saved_cities": [
        {
            "name": "北京",
            "country": "中国",
            "state": "北京市",
            "latitude": 39.9042,
            "longitude": 116.4074,
            "timezone": "Asia/Shanghai"
        },
        {
            "name": "上海",
            "country": "中国",
            "state": "上海市",
            "latitude": 31.2222,
            "longitude": 121.4581,
            "timezone": "Asia/Shanghai"
        },
        {
            "name": "广州",
            "country": "中国",
            "state": "广东省",
            "latitude": 23.1167,
            "longitude": 113.25,
            "timezone": "Asia/Shanghai"
        }
    ],
    "unit": "metric",            # 'metric' or 'imperial'
    "icon_theme": "default",      # 'default' or 'material'
    "theme_mode": "Auto",         # 'Auto', 'Light', 'Dark'
    "font_family": "系统默认 (Segoe UI / 微软雅黑)",
    "font_size": "标准 (100%)",
    "auto_refresh_minutes": 30,
}

class SettingsManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SettingsManager, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    return {**DEFAULT_SETTINGS, **loaded}
            except Exception:
                pass
        return DEFAULT_SETTINGS.copy()

    def save(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

    @property
    def selected_city(self) -> Location:
        raw = self.data.get("selected_city", DEFAULT_SETTINGS["selected_city"])
        return Location(**raw)

    @selected_city.setter
    def selected_city(self, loc: Location):
        self.data["selected_city"] = {
            "name": loc.name,
            "country": loc.country,
            "state": loc.state,
            "latitude": loc.latitude,
            "longitude": loc.longitude,
            "timezone": loc.timezone,
        }
        self.save()

    @property
    def saved_cities(self) -> List[Location]:
        raw_list = self.data.get("saved_cities", DEFAULT_SETTINGS["saved_cities"])
        return [Location(**item) for item in raw_list]

    def add_saved_city(self, loc: Location):
        cities = self.saved_cities
        for c in cities:
            if abs(c.latitude - loc.latitude) < 0.05 and abs(c.longitude - loc.longitude) < 0.05:
                return
        
        if len(self.data["saved_cities"]) >= 7:
            # Optionally remove the oldest or just return
            # Here we just return so user cannot add more than 7 without deleting
            return

        self.data["saved_cities"].append({
            "name": loc.name,
            "country": loc.country,
            "state": loc.state,
            "latitude": loc.latitude,
            "longitude": loc.longitude,
            "timezone": loc.timezone,
        })
        self.save()

    def remove_saved_city(self, index: int):
        cities = self.data.get("saved_cities", [])
        if 0 <= index < len(cities):
            cities.pop(index)
            self.save()

    @property
    def unit(self) -> str:
        return self.data.get("unit", "metric")

    @unit.setter
    def unit(self, val: str):
        self.data["unit"] = val
        self.save()

    @property
    def theme_mode(self) -> str:
        return self.data.get("theme_mode", "Auto")

    @theme_mode.setter
    def theme_mode(self, val: str):
        self.data["theme_mode"] = val
        self.save()

    @property
    def icon_theme(self) -> str:
        return self.data.get("icon_theme", "default")

    @icon_theme.setter
    def icon_theme(self, val: str):
        self.data["icon_theme"] = val
        self.save()

    @property
    def font_family(self) -> str:
        return self.data.get("font_family", "系统默认 (Segoe UI / 微软雅黑)")

    @font_family.setter
    def font_family(self, val: str):
        self.data["font_family"] = val
        self.save()

    @property
    def font_size(self) -> str:
        return self.data.get("font_size", "标准 (100%)")

    @font_size.setter
    def font_size(self, val: str):
        self.data["font_size"] = val
        self.save()

settings = SettingsManager()
