from typing import List
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame
)
from qfluentwidgets import (
    CardWidget, StrongBodyLabel, CaptionLabel, SmoothScrollArea
)
from ..core.models import HourlyItem
from ..core.icons import render_weather_pixmap

class HourlyItemWidget(QWidget):
    """Single hour column widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(68)
        self.setFixedHeight(120)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 8, 4, 8)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)

        self.lbl_time = CaptionLabel("--:--", self)
        self.lbl_time.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_time)

        self.lbl_icon = QLabel(self)
        self.lbl_icon.setFixedSize(38, 38)
        self.lbl_icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_icon)

        self.lbl_temp = StrongBodyLabel("--°", self)
        self.lbl_temp.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_temp)

        self.lbl_prob = CaptionLabel("", self)
        self.lbl_prob.setAlignment(Qt.AlignCenter)
        self.lbl_prob.setStyleSheet("color: #3B82F6; font-size: 11px;")
        layout.addWidget(self.lbl_prob)

    def set_data(self, item: HourlyItem):
        self.lbl_time.setText(item.time_str)
        self.lbl_temp.setText(f"{round(item.temperature)}°")
        
        if item.precip_prob > 0:
            self.lbl_prob.setText(f"{item.precip_prob}%")
        else:
            self.lbl_prob.setText("")

        pix = render_weather_pixmap(item.weather_code, item.is_day, size=34)
        self.lbl_icon.setPixmap(pix)


class HourlyView(CardWidget):
    """Card containing 24-hour horizontal forecast."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(175)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(10)

        # Title
        self.lbl_title = StrongBodyLabel("24 小时预报", self)
        layout.addWidget(self.lbl_title)

        # Scroll Area
        self.scroll = SmoothScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("background: transparent;")

        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: transparent;")
        self.h_layout = QHBoxLayout(self.content_widget)
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.h_layout.setSpacing(8)
        self.h_layout.setAlignment(Qt.AlignLeft)

        self.scroll.setWidget(self.content_widget)
        layout.addWidget(self.scroll)

    def update_data(self, hourly_items: List[HourlyItem]):
        # Clear existing items
        while self.h_layout.count():
            item = self.h_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for item in hourly_items:
            w = HourlyItemWidget(self.content_widget)
            w.set_data(item)
            self.h_layout.addWidget(w)
