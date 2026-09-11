from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from qfluentwidgets import (
    TitleLabel, SubtitleLabel, StrongBodyLabel, BodyLabel, CaptionLabel,
    CardWidget, ComboBox, PushButton, PrimaryPushButton, FluentIcon,
    setTheme, Theme, isDarkTheme, InfoBar, InfoBarPosition, SmoothScrollArea
)
from ..core.settings import settings
from ..core.font_manager import FONT_FAMILIES_MAP, FONT_SIZES_MAP, apply_font_settings
from ..core.theme_manager import THEMES, apply_theme

class SettingGroupCard(CardWidget):
    """Card containing multiple setting rows."""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.layout_root = QVBoxLayout(self)
        self.layout_root.setContentsMargins(20, 16, 20, 16)
        self.layout_root.setSpacing(14)

        lbl_title = StrongBodyLabel(title, self)
        self.layout_root.addWidget(lbl_title)

    def add_row(self, title: str, subtitle: str, widget: QWidget):
        row = QHBoxLayout()
        row.setContentsMargins(0, 4, 0, 4)

        info = QVBoxLayout()
        info.setSpacing(2)
        lbl_t = BodyLabel(title, self)
        info.addWidget(lbl_t)

        if subtitle:
            lbl_s = CaptionLabel(subtitle, self)
            info.addWidget(lbl_s)

        row.addLayout(info, 1)
        row.addWidget(widget)
        self.layout_root.addLayout(row)


class SettingInterface(QWidget):
    """Settings interface for units, theme, and about information."""

    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settingInterface")
        self.init_ui()

    def init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(36, 24, 36, 24)
        root_layout.setSpacing(20)

        # 1. Header
        header_box = QVBoxLayout()
        header_box.setSpacing(4)
        title = TitleLabel("偏好设置", self)
        header_box.addWidget(title)

        subtitle = CaptionLabel("个性化配置温度单位、视觉主题及天气数据源", self)
        header_box.addWidget(subtitle)
        root_layout.addLayout(header_box)

        # Scroll Area
        self.scroll = SmoothScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("background: transparent;")

        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(16)

        # 1. Units Group
        group_unit = SettingGroupCard("度量与单位", self.content_widget)
        self.combo_unit = ComboBox(group_unit)
        self.combo_unit.addItems(["公制 / 摄氏度 (°C, km/h)", "英制 / 华氏度 (°F, mph)"])
        self.combo_unit.setCurrentIndex(0 if settings.unit == "metric" else 1)
        self.combo_unit.currentIndexChanged.connect(self._on_unit_changed)
        group_unit.add_row("温标与风速单位", "选择主界面与预报中使用的测量标准", self.combo_unit)
        self.content_layout.addWidget(group_unit)

        # 2. Appearance Group
        group_theme = SettingGroupCard("外观与风格", self.content_widget)
        
        self.combo_theme = ComboBox(group_theme)
        theme_keys = list(THEMES.keys())
        self.combo_theme.addItems(theme_keys)
        curr_theme = settings.theme_mode
        selected_idx = 0
        for i, k in enumerate(theme_keys):
            if k == curr_theme or (curr_theme == "Dark" and "默认深色" in k) or (curr_theme == "Light" and "默认浅色" in k) or (curr_theme == "Auto" and "Auto" in k):
                selected_idx = i
                break
        self.combo_theme.setCurrentIndex(selected_idx)
        self.combo_theme.currentIndexChanged.connect(self._on_theme_changed)
        group_theme.add_row("应用主题配色", "切换经典极客暗色调（Catppuccin、Dracula、Nord等）或系统默认风格", self.combo_theme)

        self.combo_icons = ComboBox(group_theme)
        self.combo_icons.addItems(["经典渐变风格 (Default)", "Material 扁平风格 (Material)"])
        self.combo_icons.setCurrentIndex(0 if settings.icon_theme == "default" else 1)
        self.combo_icons.currentIndexChanged.connect(self._on_icon_changed)
        group_theme.add_row("天气图标主题", "切换天气状态矢量图标视觉风格", self.combo_icons)
        self.content_layout.addWidget(group_theme)

        # 3. Typography Group
        group_font = SettingGroupCard("字体与文字大小", self.content_widget)

        self.combo_font_family = ComboBox(group_font)
        font_keys = list(FONT_FAMILIES_MAP.keys())
        self.combo_font_family.addItems(font_keys)
        curr_family = settings.font_family
        if curr_family in font_keys:
            self.combo_font_family.setCurrentIndex(font_keys.index(curr_family))
        self.combo_font_family.currentIndexChanged.connect(self._on_font_family_changed)
        group_font.add_row("界面字体", "自定义应用的文本显示字体族", self.combo_font_family)

        self.combo_font_size = ComboBox(group_font)
        size_keys = list(FONT_SIZES_MAP.keys())
        self.combo_font_size.addItems(size_keys)
        curr_size = settings.font_size
        if curr_size in size_keys:
            self.combo_font_size.setCurrentIndex(size_keys.index(curr_size))
        self.combo_font_size.currentIndexChanged.connect(self._on_font_size_changed)
        group_font.add_row("文字大小", "全局缩放应用内文字与卡片排版字号", self.combo_font_size)
        self.content_layout.addWidget(group_font)

        # 4. About Group
        group_about = SettingGroupCard("关于 Mousam Windows", self.content_widget)
        
        row_about = QVBoxLayout()
        row_about.setSpacing(6)
        
        lbl_v = StrongBodyLabel("Mousam Windows v2.1.0", group_about)
        row_about.addWidget(lbl_v)
        
        lbl_desc = CaptionLabel(
            "本项目基于 Linux 知名开源天气应用 Mousam 深度重构，保留其完整的数据请求逻辑与精美图标设计，"
            "并结合 Windows 11 Fluent Design（云母亚克力磨砂、现代卡片化排版）打造原生的 Windows 天气桌面应用。\n\n"
            "• 上游项目：github.com/amit9838/mousam (GPL-3.0)\n"
            "• 天气数据：由 Open-Meteo (open-meteo.com) 免费开源提供\n"
            "• 图标设计：由 @basmilius 设计制作",
            group_about
        )
        lbl_desc.setWordWrap(True)
        row_about.addWidget(lbl_desc)
        group_about.layout_root.addLayout(row_about)
        self.content_layout.addWidget(group_about)

        self.content_layout.addStretch()
        self.scroll.setWidget(self.content_widget)
        root_layout.addWidget(self.scroll, 1)

    def _on_unit_changed(self, idx: int):
        settings.unit = "metric" if idx == 0 else "imperial"
        self.settings_changed.emit()

    def _on_theme_changed(self, idx: int):
        chosen = self.combo_theme.currentText()
        settings.theme_mode = chosen
        apply_theme(chosen, window=self.window())
        self.settings_changed.emit()

    def _on_icon_changed(self, idx: int):
        settings.icon_theme = "default" if idx == 0 else "material"
        self.settings_changed.emit()

    def _on_font_family_changed(self, idx: int):
        family_name = self.combo_font_family.currentText()
        settings.font_family = family_name
        apply_font_settings(family_key=family_name, window=self.window())
        self.settings_changed.emit()

    def _on_font_size_changed(self, idx: int):
        size_name = self.combo_font_size.currentText()
        settings.font_size = size_name
        apply_font_settings(size_key=size_name, window=self.window())
        self.settings_changed.emit()
