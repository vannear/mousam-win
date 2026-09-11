from PyQt5.QtCore import QThread, pyqtSignal
from .models import Location, FullWeatherData
from .api import fetch_full_weather

class WeatherWorker(QThread):
    """Background worker thread for non-blocking weather data fetching."""

    data_fetched = pyqtSignal(FullWeatherData)
    fetch_failed = pyqtSignal(str)

    def __init__(self, location: Location, unit: str = "metric", parent=None):
        super().__init__(parent)
        self.location = location
        self.unit = unit

    def run(self):
        try:
            data = fetch_full_weather(self.location, self.unit)
            self.data_fetched.emit(data)
        except Exception as e:
            self.fetch_failed.emit(str(e))
