from typing import List, Dict
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QFont
from qfluentwidgets import setFontFamilies, FluentLabelBase
import qfluentwidgets.common.font as qfont
import qfluentwidgets.components.widgets.label as qlabel

FONT_FAMILIES_MAP: Dict[str, List[str]] = {
    "系统默认 (Segoe UI / 微软雅黑)": ["Segoe UI", "Microsoft YaHei UI", "PingFang SC"],
    "微软雅黑 (Microsoft YaHei)": ["Microsoft YaHei UI", "Microsoft YaHei"],
    "Segoe UI (现代西文)": ["Segoe UI", "Microsoft YaHei UI"],
    "等线 (DengXian)": ["DengXian", "Microsoft YaHei UI"],
    "楷体 (KaiTi)": ["KaiTi", "STKaiti", "Microsoft YaHei UI"],
    "宋体 (SimSun)": ["SimSun", "STSong", "Microsoft YaHei UI"],
    "黑体 (SimHei)": ["SimHei", "STHeiti", "Microsoft YaHei UI"],
    "仿宋 (FangSong)": ["FangSong", "STFangsong", "Microsoft YaHei UI"],
}

FONT_SIZES_MAP: Dict[str, float] = {
    "小 (90%)": 0.9,
    "标准 (100%)": 1.0,
    "偏大 (110%)": 1.1,
    "大 (120%)": 1.2,
    "超大 (130%)": 1.3,
}

_orig_get_font = qfont.getFont
_current_scale = 1.0

def _scaled_get_font(fontSize=14, weight=QFont.Normal):
    scaled_size = max(10, int(round(fontSize * _current_scale)))
    return _orig_get_font(scaled_size, weight)

# Monkey-patch getFont so all newly created/queried Fluent labels scale
qfont.getFont = _scaled_get_font
qlabel.getFont = _scaled_get_font

def apply_font_settings(family_key: str = None, size_key: str = None, window: QWidget = None):
    """Apply font family and size scaling globally across all UI components."""
    global _current_scale
    from .settings import settings

    if family_key is None:
        family_key = settings.font_family
    if size_key is None:
        size_key = settings.font_size

    _current_scale = FONT_SIZES_MAP.get(size_key, 1.0)
    families = FONT_FAMILIES_MAP.get(family_key, FONT_FAMILIES_MAP["系统默认 (Segoe UI / 微软雅黑)"])

    # 1. Update Fluent font families
    setFontFamilies(families)

    # 2. Update QApplication global font
    app = QApplication.instance()
    if app:
        base_font = app.font()
        if families:
            base_font.setFamily(families[0])
            base_font.setFamilies(families)
        base_pt = int(round(9 * _current_scale))
        base_font.setPointSize(max(8, base_pt))
        app.setFont(base_font)

    # 3. Update all existing Fluent labels in window if provided
    if window:
        for lbl in window.findChildren(FluentLabelBase):
            try:
                lbl.setFont(lbl.getFont())
            except Exception:
                pass
        window.update()
