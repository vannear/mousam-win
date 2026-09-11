from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from qfluentwidgets import (
    CardWidget, TitleLabel, StrongBodyLabel, BodyLabel, CaptionLabel, ProgressBar
)
from ..core.models import CurrentWeather, DailyItem, AirQuality
from ..core.configs import get_uv_level

class MetricCard(CardWidget):
    """Reusable metric card component."""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setFixedHeight(140)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(6)

        # Title
        self.lbl_title = CaptionLabel(title, self)
        layout.addWidget(self.lbl_title)

        # Main Value + Level
        val_box = QHBoxLayout()
        val_box.setSpacing(8)
        self.lbl_value = TitleLabel("--", self)
        val_box.addWidget(self.lbl_value)

        self.lbl_tag = CaptionLabel("", self)
        self.lbl_tag.setStyleSheet(
            "padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 12px; color: white;"
        )
        self.lbl_tag.hide()
        val_box.addWidget(self.lbl_tag)
        val_box.addStretch()
        layout.addLayout(val_box)

        # Subtext 1
        self.lbl_sub1 = BodyLabel("", self)
        layout.addWidget(self.lbl_sub1)

        # Subtext 2
        self.lbl_sub2 = CaptionLabel("", self)
        layout.addWidget(self.lbl_sub2)

    def set_content(self, value: str, tag: str = "", tag_color: str = "", sub1: str = "", sub2: str = ""):
        self.lbl_value.setText(value)
        if tag:
            self.lbl_tag.setText(tag)
            self.lbl_tag.setStyleSheet(
                f"background-color: {tag_color}; padding: 2px 8px; border-radius: 6px; font-weight: 600; font-size: 12px; color: white;"
            )
            self.lbl_tag.show()
        else:
            self.lbl_tag.hide()

        self.lbl_sub1.setText(sub1)
        self.lbl_sub2.setText(sub2)


class MetricsGrid(QWidget):
    """Grid displaying 6 detailed weather metrics."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # 1. AQI
        self.card_aqi = MetricCard("空气质量 (AQI)", self)
        layout.addWidget(self.card_aqi, 0, 0)

        # 2. UV Index
        self.card_uv = MetricCard("紫外线指数", self)
        layout.addWidget(self.card_uv, 0, 1)

        # 3. Wind
        self.card_wind = MetricCard("风速与风向", self)
        layout.addWidget(self.card_wind, 0, 2)

        # 4. Humidity
        self.card_humidity = MetricCard("湿度与体感", self)
        layout.addWidget(self.card_humidity, 1, 0)

        # 5. Pressure
        self.card_pressure = MetricCard("气压", self)
        layout.addWidget(self.card_pressure, 1, 1)

        # 6. Sun
        self.card_sun = MetricCard("日出与日落", self)
        layout.addWidget(self.card_sun, 1, 2)

    def update_data(self, current: CurrentWeather, daily: list, aq: AirQuality, unit: str = "metric"):
        # 1. AQI
        if aq:
            self.card_aqi.set_content(
                value=str(aq.aqi),
                tag=aq.level_text,
                tag_color=aq.level_color,
                sub1=f"PM2.5: {aq.pm2_5} · PM10: {aq.pm10}",
                sub2=f"O₃: {aq.o3} · NO₂: {aq.no2} µg/m³"
            )
        else:
            self.card_aqi.set_content("暂无数据", sub1="未获取到当地空气质量")

        # 2. UV
        uv_val = current.uv_index
        uv_text, uv_col = get_uv_level(uv_val)
        uv_advice = "无需防晒" if uv_val <= 2 else ("建议涂抹防晒霜" if uv_val <= 5 else "尽量避免正午暴晒")
        self.card_uv.set_content(
            value=f"{uv_val}",
            tag=uv_text,
            tag_color=uv_col,
            sub1=uv_advice,
            sub2="最高值通常出现在中午 12:00 - 14:00"
        )

        # 3. Wind
        wind_unit_str = "mph" if unit == "imperial" else "km/h"
        dirs = ["北", "东北偏北", "东北", "东北偏东", "东", "东南偏东", "东南", "东南偏南", 
                "南", "西南偏南", "西南", "西南偏西", "西", "西北偏西", "西北", "西北偏北"]
        idx = int((current.wind_direction + 11.25) / 22.5) % 16
        dir_str = dirs[idx]
        
        # Beaufort scale approximate
        ws = current.wind_speed
        scale = "微风" if ws < 12 else ("和风" if ws < 20 else ("清劲" if ws < 30 else "强风"))
        self.card_wind.set_content(
            value=f"{ws} {wind_unit_str}",
            sub1=f"{dir_str} ({current.wind_direction}°)",
            sub2=f"风力状态: {scale}"
        )

        # 4. Humidity
        hum = current.humidity
        hum_status = "干燥" if hum < 30 else ("适宜舒适" if hum <= 65 else "潮湿")
        self.card_humidity.set_content(
            value=f"{hum}%",
            sub1=f"环境感觉: {hum_status}",
            sub2=f"当前降水量: {current.precipitation} mm"
        )

        # 5. Pressure
        press_unit = "inHg" if unit == "imperial" else "hPa"
        self.card_pressure.set_content(
            value=f"{current.pressure} {press_unit}",
            sub1="正常标准大气压范围",
            sub2="气压稳定，无剧烈突变"
        )

        # 6. Sun
        sr = daily[0].sunrise_str if daily else "--:--"
        ss = daily[0].sunset_str if daily else "--:--"
        self.card_sun.set_content(
            value=f"🌅 {sr}",
            sub1=f"🌇 日落: {ss}",
            sub2="提供自然日光变化参考"
        )
