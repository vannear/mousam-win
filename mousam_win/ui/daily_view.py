from typing import List
from PyQt5.QtCore import Qt, QRectF, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QLinearGradient, QBrush
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from qfluentwidgets import (
    CardWidget, StrongBodyLabel, BodyLabel, CaptionLabel
)
from ..core.models import DailyItem
from ..core.icons import render_weather_pixmap

class TempRangeBar(QWidget):
    """Custom bar widget visualizing min-to-max temperature range relative to the weekly span."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(12)
        self.t_min = 10
        self.t_max = 25
        self.w_min = 5
        self.w_max = 30

    def set_range(self, t_min: float, t_max: float, w_min: float, w_max: float):
        self.t_min = t_min
        self.t_max = t_max
        self.w_min = w_min
        self.w_max = max(w_max, w_min + 1)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        w = self.width()
        h = self.height()
        radius = h / 2

        # 1. Background Track
        track_rect = QRectF(0, 0, w, h)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(128, 128, 128, 40))
        painter.drawRoundedRect(track_rect, radius, radius)

        # 2. Active Temperature Range
        span = self.w_max - self.w_min
        start_ratio = max(0.0, min(1.0, (self.t_min - self.w_min) / span))
        end_ratio = max(0.0, min(1.0, (self.t_max - self.w_min) / span))

        bar_x = start_ratio * w
        bar_w = max(h, (end_ratio - start_ratio) * w)
        if bar_x + bar_w > w:
            bar_w = w - bar_x

        # Gradient from cool to warm
        grad = QLinearGradient(0, 0, w, 0)
        grad.setColorAt(0.0, QColor("#38BDF8"))  # Cool Cyan
        grad.setColorAt(0.5, QColor("#FBBF24"))  # Warm Amber
        grad.setColorAt(1.0, QColor("#F87171"))  # Soft Red

        active_rect = QRectF(bar_x, 0, bar_w, h)
        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(active_rect, radius, radius)
        painter.end()


class DailyRowWidget(QWidget):
    """Single row for one day in the 10-day forecast."""
    clicked = pyqtSignal(int) # Emits index of the day

    def __init__(self, index: int, parent=None):
        super().__init__(parent)
        self.index = index
        self.setFixedHeight(44)
        # Enable cursor change on hover
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 4, 12, 4)
        layout.setSpacing(12)

        # 1. Day / Date
        self.lbl_day = StrongBodyLabel("今天", self)
        self.lbl_day.setFixedWidth(75)
        layout.addWidget(self.lbl_day)

        # 2. Icon + Condition
        self.lbl_icon = QLabel(self)
        self.lbl_icon.setFixedSize(30, 30)
        layout.addWidget(self.lbl_icon)

        self.lbl_condition = BodyLabel("晴朗", self)
        self.lbl_condition.setFixedWidth(100)
        layout.addWidget(self.lbl_condition)

        # 3. Rain Probability
        self.lbl_rain = CaptionLabel("", self)
        self.lbl_rain.setFixedWidth(55)
        self.lbl_rain.setStyleSheet("color: #3B82F6; font-weight: 500;")
        layout.addWidget(self.lbl_rain)

        # 4. Min Temp Label
        self.lbl_min = CaptionLabel("15°", self)
        self.lbl_min.setFixedWidth(30)
        self.lbl_min.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.lbl_min)

        # 5. Temperature Range Visual Bar
        self.temp_bar = TempRangeBar(self)
        layout.addWidget(self.temp_bar, 1)

        # 6. Max Temp Label
        self.lbl_max = StrongBodyLabel("25°", self)
        self.lbl_max.setFixedWidth(30)
        self.lbl_max.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(self.lbl_max)

    def set_data(self, item: DailyItem, week_min: float, week_max: float):
        self.lbl_day.setText(f"{item.weekday}")
        self.lbl_condition.setText(item.condition_text)
        
        if item.precip_prob_max > 0:
            self.lbl_rain.setText(f"💧{item.precip_prob_max}%")
        else:
            self.lbl_rain.setText("")

        self.lbl_min.setText(f"{round(item.temp_min)}°")
        self.lbl_max.setText(f"{round(item.temp_max)}°")

        pix = render_weather_pixmap(item.weather_code, 1, size=28)
        self.lbl_icon.setPixmap(pix)

        self.temp_bar.set_range(item.temp_min, item.temp_max, week_min, week_max)
        
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.index)


class DailyView(CardWidget):
    """Card containing 10-day forecast."""
    day_clicked = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.layout_root = QVBoxLayout(self)
        self.layout_root.setContentsMargins(20, 16, 20, 16)
        self.layout_root.setSpacing(6)

        self.lbl_title = StrongBodyLabel("未来 7 天天气预报", self)
        self.layout_root.addWidget(self.lbl_title)

        self.rows_container = QVBoxLayout()
        self.rows_container.setSpacing(2)
        self.layout_root.addLayout(self.rows_container)

    def update_data(self, daily_items: List[DailyItem]):
        # Clear existing rows
        while self.rows_container.count():
            item = self.rows_container.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not daily_items:
            return

        week_min = min(item.temp_min for item in daily_items)
        week_max = max(item.temp_max for item in daily_items)

        for i, item in enumerate(daily_items):
            row = DailyRowWidget(i, self)
            row.set_data(item, week_min, week_max)
            row.clicked.connect(self.day_clicked.emit)
            self.rows_container.addWidget(row)
