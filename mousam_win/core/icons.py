import os
from pathlib import Path
from PyQt5.QtGui import QPixmap, QPainter, QIcon
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtCore import Qt, QSize
from .configs import DEFAULT_ICONS_DIR, MATERIAL_ICONS_DIR, WMO_CODE_ICON, WMO_CODE_TEXT

# Cache for rendered pixmaps
_pixmap_cache = {}

def get_icon_path(weather_code: int, is_day: int = 1, theme: str = "default") -> str:
    """Return the SVG file path for a weather code and day/night status."""
    base_dir = MATERIAL_ICONS_DIR if theme == "material" else DEFAULT_ICONS_DIR
    
    code_str = str(weather_code)
    if is_day == 0:
        night_key = f"{code_str}n"
        if night_key in WMO_CODE_ICON:
            candidate = base_dir / WMO_CODE_ICON[night_key]
            if candidate.exists():
                return str(candidate)

    filename = WMO_CODE_ICON.get(code_str, "clear-day.svg")
    target = base_dir / filename
    if target.exists():
        return str(target)
    
    # Fallback to clear-day
    return str(base_dir / "clear-day.svg")

def get_weather_desc(weather_code: int) -> str:
    """Return Chinese description of weather code."""
    return WMO_CODE_TEXT.get(weather_code, "多云")

def render_weather_pixmap(weather_code: int, is_day: int = 1, size: int = 64, theme: str = "default") -> QPixmap:
    """Render weather SVG icon to a transparent QPixmap."""
    cache_key = (weather_code, is_day, size, theme)
    if cache_key in _pixmap_cache:
        return _pixmap_cache[cache_key]

    path = get_icon_path(weather_code, is_day, theme)
    renderer = QSvgRenderer(path)
    
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
    renderer.render(painter)
    painter.end()

    _pixmap_cache[cache_key] = pixmap
    return pixmap

def render_weather_icon(weather_code: int, is_day: int = 1, size: int = 64, theme: str = "default") -> QIcon:
    """Return QIcon of rendered weather SVG."""
    return QIcon(render_weather_pixmap(weather_code, is_day, size, theme))
