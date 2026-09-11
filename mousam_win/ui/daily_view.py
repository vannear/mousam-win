from typing import List
from PyQt5.QtCore import Qt, QRectF, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPainter, QColor, QLinearGradient, QBrush
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from qfluentwidgets import (
    CardWidget, StrongBodyLabel, BodyLabel, CaptionLabel, SmoothScrollArea
)
from ..core.models import DailyItem, HourlyItem
from ..core.icons import render_weather_pixmap
from .hourly_view import HourlyItemWidget

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
    """Single row for one day in the 10-day forecast with inline expandable 24-hour view."""
    toggled = pyqtSignal() # Emits when expanded state changes

    def __init__(self, index: int, parent=None):
        super().__init__(parent)
        self.index = index
        self.is_expanded = False
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # --- 1. Top row (Always visible) ---
        self.row_widget = QWidget(self)
        self.row_widget.setFixedHeight(44)
        self.row_widget.setCursor(Qt.PointingHandCursor)
        
        row_layout = QHBoxLayout(self.row_widget)
        row_layout.setContentsMargins(12, 4, 12, 4)
        row_layout.setSpacing(12)

        self.lbl_day = StrongBodyLabel("今天", self.row_widget)
        self.lbl_day.setFixedWidth(75)
        row_layout.addWidget(self.lbl_day)

        self.lbl_icon = QLabel(self.row_widget)
        self.lbl_icon.setFixedSize(30, 30)
        row_layout.addWidget(self.lbl_icon)

        self.lbl_condition = BodyLabel("晴朗", self.row_widget)
        self.lbl_condition.setFixedWidth(100)
        row_layout.addWidget(self.lbl_condition)

        self.lbl_rain = CaptionLabel("", self.row_widget)
        self.lbl_rain.setFixedWidth(55)
        self.lbl_rain.setStyleSheet("color: #3B82F6; font-weight: 500;")
        row_layout.addWidget(self.lbl_rain)

        self.lbl_min = CaptionLabel("15°", self.row_widget)
        self.lbl_min.setFixedWidth(30)
        self.lbl_min.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        row_layout.addWidget(self.lbl_min)

        self.temp_bar = TempRangeBar(self.row_widget)
        row_layout.addWidget(self.temp_bar, 1)

        self.lbl_max = StrongBodyLabel("25°", self.row_widget)
        self.lbl_max.setFixedWidth(30)
        self.lbl_max.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        row_layout.addWidget(self.lbl_max)
        
        self.main_layout.addWidget(self.row_widget)
        
        # --- 2. Expandable Hourly Area (Hidden by default) ---
        self.expand_widget = QWidget(self)
        self.expand_widget.setFixedHeight(0) # Initially collapsed
        self.expand_widget.setStyleSheet("background: transparent;")
        
        expand_layout = QVBoxLayout(self.expand_widget)
        expand_layout.setContentsMargins(0, 10, 0, 10)
        
        self.scroll = SmoothScrollArea(self.expand_widget)
        self.scroll.setFixedHeight(140)
        self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("background: transparent;")

        self.hourly_content = QWidget()
        self.hourly_content.setStyleSheet("background: transparent;")
        self.h_layout = QHBoxLayout(self.hourly_content)
        self.h_layout.setContentsMargins(12, 0, 12, 0)
        self.h_layout.setSpacing(8)
        self.h_layout.setAlignment(Qt.AlignLeft)

        self.scroll.setWidget(self.hourly_content)
        expand_layout.addWidget(self.scroll)
        
        self.main_layout.addWidget(self.expand_widget)

    def set_data(self, item: DailyItem, week_min: float, week_max: float, hourly_slice: List[HourlyItem] = None):
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
        
        # Populate hourly data if provided
        while self.h_layout.count():
            w_item = self.h_layout.takeAt(0)
            if w_item.widget():
                w_item.widget().deleteLater()
                
        if hourly_slice:
            for h in hourly_slice:
                w = HourlyItemWidget(self.hourly_content)
                w.set_data(h)
                self.h_layout.addWidget(w)
        
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            # We must determine if click was inside the row_widget, not the scroll area
            if self.row_widget.geometry().contains(event.pos()):
                self._toggle_expand()

    def _toggle_expand(self):
        self.is_expanded = not self.is_expanded
        
        # Simple height animation
        target_h = 160 if self.is_expanded else 0
        
        self.anim = QPropertyAnimation(self.expand_widget, b"maximumHeight", self)
        self.anim.setDuration(300)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.setStartValue(self.expand_widget.height())
        self.anim.setEndValue(target_h)
        self.anim.start()
        
        self.toggled.emit()


class DailyView(CardWidget):
    """Card containing 10-day forecast with inline expandable hours."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.layout_root = QVBoxLayout(self)
        self.layout_root.setContentsMargins(20, 16, 20, 16)
        self.layout_root.setSpacing(6)

        self.lbl_title = StrongBodyLabel("未来 10 天天气预报 (点击展开24小时详情)", self)
        self.layout_root.addWidget(self.lbl_title)

        self.rows_container = QVBoxLayout()
        self.rows_container.setSpacing(2)
        self.layout_root.addLayout(self.rows_container)

    def update_data(self, daily_items: List[DailyItem], hourly_items: List['HourlyItem'] = None):
        # Clear existing rows
        while self.rows_container.count():
            item = self.rows_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not daily_items:
            return

        week_min = min(item.temp_min for item in daily_items)
        week_max = max(item.temp_max for item in daily_items)

        for i, item in enumerate(daily_items):
            row = DailyRowWidget(i, self)
            
            # Extract 24-hour slice for this specific day
            h_slice = None
            if hourly_items:
                start_idx = i * 24
                end_idx = start_idx + 24
                h_slice = hourly_items[start_idx:end_idx]
                
            row.set_data(item, week_min, week_max, h_slice)
            
            # When toggled, we can optionally collapse others (accordion style)
            row.toggled.connect(lambda i=i: self._on_row_toggled(i))
            
            self.rows_container.addWidget(row)
            
    def _on_row_toggled(self, expanded_index: int):
        # Optional: Collapse other rows
        for i in range(self.rows_container.count()):
            if i == expanded_index:
                continue
            item = self.rows_container.itemAt(i)
            if item and item.widget():
                row = item.widget()
                if row.is_expanded:
                    row.is_expanded = False
                    row.expand_widget.setMaximumHeight(0)
