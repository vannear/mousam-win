from datetime import datetime
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from qfluentwidgets import (
    ScrollArea, SmoothScrollArea, TitleLabel, SubtitleLabel,
    CaptionLabel, PrimaryPushButton, ToolButton, FluentIcon,
    InfoBar, InfoBarPosition, IndeterminateProgressBar
)

from ..core.models import Location, FullWeatherData
from ..core.settings import settings
from ..core.worker import WeatherWorker
from .current_card import CurrentCard
from .hourly_view import HourlyView
from .daily_view import DailyView
from .metrics_grid import MetricsGrid

class WeatherInterface(QWidget):
    """Main weather dashboard interface."""

    request_city_switch = pyqtSignal()

    def __init__(self, location: Location = None, parent=None):
        super().__init__(parent)
        self.location = location
        self.setObjectName(f"weatherInterface_{id(self)}")
        self.worker: WeatherWorker = None
        self.current_data: FullWeatherData = None

        self.init_ui()

    def init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. Top Header Area
        self.header_widget = QWidget(self)
        self.header_widget.setFixedHeight(88)
        header_layout = QHBoxLayout(self.header_widget)
        header_layout.setContentsMargins(36, 16, 36, 12)

        # Left: City & Region
        city_box = QVBoxLayout()
        city_box.setSpacing(2)
        self.lbl_city = TitleLabel("北京", self)
        city_box.addWidget(self.lbl_city)

        self.lbl_region = CaptionLabel("中国 · 北京市", self)
        city_box.addWidget(self.lbl_region)
        header_layout.addLayout(city_box)

        header_layout.addStretch()

        # Right: Action Buttons
        actions_box = QHBoxLayout()
        actions_box.setSpacing(10)

        self.lbl_updated = CaptionLabel("准备就绪", self)
        actions_box.addWidget(self.lbl_updated)

        self.btn_unit = ToolButton(self)
        self.btn_unit.setText("°C")
        self.btn_unit.setToolTip("切换温标 (°C / °F)")
        self.btn_unit.clicked.connect(self._toggle_unit)
        actions_box.addWidget(self.btn_unit)

        self.btn_search = ToolButton(FluentIcon.SEARCH, self)
        self.btn_search.setToolTip("搜索或切换城市")
        self.btn_search.clicked.connect(lambda: self.request_city_switch.emit())
        actions_box.addWidget(self.btn_search)

        self.btn_refresh = PrimaryPushButton("刷新", self, FluentIcon.SYNC)
        self.btn_refresh.setFixedWidth(90)
        self.btn_refresh.clicked.connect(self.refresh)
        actions_box.addWidget(self.btn_refresh)

        header_layout.addLayout(actions_box)
        root_layout.addWidget(self.header_widget)

        # Loading Progress Bar
        self.progress_bar = IndeterminateProgressBar(self)
        self.progress_bar.setFixedHeight(3)
        self.progress_bar.hide()
        root_layout.addWidget(self.progress_bar)

        # 2. Main Scroll Area for Weather Cards
        self.scroll = SmoothScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("background: transparent;")

        self.cards_container = QWidget()
        self.cards_container.setStyleSheet("background: transparent;")
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(36, 12, 36, 36)
        self.cards_layout.setSpacing(20)

        # Card 1: Current Weather
        self.card_current = CurrentCard(self.cards_container)
        self.cards_layout.addWidget(self.card_current)

        # Card 2: 24-Hour Forecast
        self.card_hourly = HourlyView(self.cards_container)
        self.cards_layout.addWidget(self.card_hourly)

        # Card 3: 7-Day Forecast
        self.card_daily = DailyView(self.cards_container)
        self.cards_layout.addWidget(self.card_daily)

        # Card 4: Metrics Grid
        self.grid_metrics = MetricsGrid(self.cards_container)
        self.cards_layout.addWidget(self.grid_metrics)

        self.scroll.setWidget(self.cards_container)
        root_layout.addWidget(self.scroll, 1)

    def load_weather(self, location: Location = None):
        """Fetch weather data in background thread."""
        loc = location or self.location or settings.selected_city
        self.location = loc
        unit = settings.unit

        self.lbl_city.setText(loc.name)
        self.lbl_region.setText(loc.display_name)
        self.btn_unit.setText("°F" if unit == "imperial" else "°C")

        # Start loading animation
        self.progress_bar.show()
        self.progress_bar.start()
        self.btn_refresh.setEnabled(False)

        # Start worker thread
        self.worker = WeatherWorker(loc, unit, self)
        self.worker.data_fetched.connect(self._on_data_fetched)
        self.worker.fetch_failed.connect(self._on_fetch_failed)
        self.worker.start()

    def refresh(self):
        self.load_weather(self.location)

    def _toggle_unit(self):
        new_unit = "imperial" if settings.unit == "metric" else "metric"
        settings.unit = new_unit
        self.btn_unit.setText("°F" if new_unit == "imperial" else "°C")
        self.refresh()

    def _on_data_fetched(self, data: FullWeatherData):
        self.progress_bar.stop()
        self.progress_bar.hide()
        self.btn_refresh.setEnabled(True)
        self.current_data = data

        # Update Header
        now_str = datetime.now().strftime("%H:%M")
        self.lbl_updated.setText(f"已于 {now_str} 更新")

        # Update Cards
        self.card_current.update_data(data.current, data.daily, data.location, settings.unit)
        
        # Initial: Next 24 hours
        start_idx = 0
        for i, h in enumerate(data.hourly):
            if h.time_str == "现在" or h.timestamp >= data.current.timestamp if hasattr(data.current, 'timestamp') else False:
                # Wait, time_str is set to "现在" for the current hour in api.py
                pass
        
        # We can find start_idx by looking for "现在" or just use the first item if not found
        start_idx = next((i for i, h in enumerate(data.hourly) if h.time_str == "现在"), 0)
        self.card_hourly.update_data(data.hourly[start_idx:start_idx + 24])
        self.card_daily.update_data(data.daily, data.hourly)
        self.grid_metrics.update_data(data.current, data.daily, data.air_quality, settings.unit)


    def _on_fetch_failed(self, error_msg: str):
        self.progress_bar.stop()
        self.progress_bar.hide()
        self.btn_refresh.setEnabled(True)
        self.lbl_updated.setText("获取天气失败")

        InfoBar.error(
            title="数据获取错误",
            content=f"未能连接至天气服务: {error_msg}",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=4000,
            parent=self
        )
