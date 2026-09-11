from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from qfluentwidgets import (
    ElevatedCardWidget, SubtitleLabel, TitleLabel, BodyLabel,
    CaptionLabel, DisplayLabel, FluentIcon, IconWidget
)
from ..core.models import CurrentWeather, DailyItem, Location
from ..core.icons import render_weather_pixmap

class CurrentCard(ElevatedCardWidget):
    """Card displaying current weather conditions with large typography and dynamic icon."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CurrentCard")
        self.setFixedHeight(180)
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(28, 20, 28, 20)
        layout.setSpacing(16)

        # Left Info Column
        left_box = QVBoxLayout()
        left_box.setSpacing(4)
        left_box.setAlignment(Qt.AlignVCenter)

        # 1. Condition and Range
        self.lbl_condition = SubtitleLabel("获取天气中...", self)
        left_box.addWidget(self.lbl_condition)

        # 2. Big Temperature
        self.lbl_temp = DisplayLabel("--°", self)
        left_box.addWidget(self.lbl_temp)

        # 3. Feels like & High/Low
        self.lbl_subtext = BodyLabel("体感 --° · 最高 --° / 最低 --°", self)
        left_box.addWidget(self.lbl_subtext)

        layout.addLayout(left_box, 1)

        # Right Icon Column
        right_box = QVBoxLayout()
        right_box.setAlignment(Qt.AlignCenter)
        self.lbl_icon = QLabel(self)
        self.lbl_icon.setFixedSize(110, 110)
        self.lbl_icon.setAlignment(Qt.AlignCenter)
        right_box.addWidget(self.lbl_icon)

        layout.addLayout(right_box)

    def update_data(self, current: CurrentWeather, daily: list, location: Location, unit: str = "metric"):
        temp_sym = "°F" if unit == "imperial" else "°C"
        
        # High and Low from daily[0]
        t_max = daily[0].temp_max if daily else current.temperature
        t_min = daily[0].temp_min if daily else current.temperature

        self.lbl_condition.setText(f"{location.name} · {current.condition_text}")
        self.lbl_temp.setText(f"{round(current.temperature)}{temp_sym}")
        self.lbl_subtext.setText(
            f"体感 {round(current.feels_like)}{temp_sym}  ·  "
            f"最高 {round(t_max)}° / 最低 {round(t_min)}°  ·  "
            f"降水 {current.precipitation} mm"
        )

        # Update Weather Icon
        pixmap = render_weather_pixmap(current.weather_code, current.is_day, size=100)
        self.lbl_icon.setPixmap(pixmap)
