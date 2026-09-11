from typing import Dict, Any, Optional
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QWidget
from qfluentwidgets import setTheme, Theme, setThemeColor, isDarkTheme

THEMES: Dict[str, Dict[str, Any]] = {
    "Catppuccin Mocha (猫普钦暗色)": {
        "mode": Theme.DARK,
        "accent": "#cba6f7",          # Mauve
        "window_bg": "#1e1e2e",       # Base
        "sidebar_bg": "#181825",      # Mantle
        "sidebar_border": "#313244",  # Surface0
        "use_mica": False,
        "desc": "温润典雅的暗色调，以柔和粉紫为强调色",
    },
    "Dracula (德古拉暗黑)": {
        "mode": Theme.DARK,
        "accent": "#bd93f9",          # Dracula Purple
        "window_bg": "#282a36",       # Background
        "sidebar_bg": "#21222c",      # Darker BG
        "sidebar_border": "#44475a",  # Current Line
        "use_mica": False,
        "desc": "经典的黑客流行暗黑配色，高对比度紫色强调",
    },
    "Nord (北欧极光深蓝)": {
        "mode": Theme.DARK,
        "accent": "#88c0d0",          # Frost Cyan
        "window_bg": "#2e3440",       # Nord0 Polar Night
        "sidebar_bg": "#242933",      # Deep Polar Night
        "sidebar_border": "#3b4252",  # Nord1
        "use_mica": False,
        "desc": "冰冷清爽的极光深蓝冷色调，护眼耐看",
    },
    "Tokyo Night (东京之夜)": {
        "mode": Theme.DARK,
        "accent": "#7aa2f7",          # Tokyo Night Blue
        "window_bg": "#1a1b26",       # Night BG
        "sidebar_bg": "#16161e",      # Deep Night
        "sidebar_border": "#2f3549",
        "use_mica": False,
        "desc": "深邃静谧的午夜蓝紫调，科技感十足",
    },
    "One Dark Pro (经典暗灰)": {
        "mode": Theme.DARK,
        "accent": "#61afef",          # Atom Blue
        "window_bg": "#21252b",       # Dark Grey
        "sidebar_bg": "#1d2026",
        "sidebar_border": "#2c313a",
        "use_mica": False,
        "desc": "经典 Atom / VS Code 现代工业暗灰调",
    },
    "Gruvbox Dark (复古暖暗)": {
        "mode": Theme.DARK,
        "accent": "#fe8019",          # Gruvbox Orange
        "window_bg": "#282828",       # Dark0
        "sidebar_bg": "#1d2021",       # Hard Dark
        "sidebar_border": "#3c3836",
        "use_mica": False,
        "desc": "复古舒适的暖调大地暗色，复古极客最爱",
    },
    "Fluent 默认深色 (Windows Dark)": {
        "mode": Theme.DARK,
        "accent": "#0078D4",
        "window_bg": "#202020",
        "sidebar_bg": "transparent",
        "sidebar_border": "rgba(255, 255, 255, 0.08)",
        "use_mica": True,
        "desc": "微软 Windows 11 原生深色磨砂云母风格",
    },
    "Fluent 默认浅色 (Windows Light)": {
        "mode": Theme.LIGHT,
        "accent": "#0078D4",
        "window_bg": "#F0F4F9",
        "sidebar_bg": "transparent",
        "sidebar_border": "rgba(0, 0, 0, 0.08)",
        "use_mica": True,
        "desc": "微软 Windows 11 原生明亮浅色风格",
    },
    "跟随系统 (Auto)": {
        "mode": Theme.AUTO,
        "accent": "#0078D4",
        "window_bg": None,
        "sidebar_bg": "transparent",
        "sidebar_border": "transparent",
        "use_mica": True,
        "desc": "根据 Windows 11 系统深色/浅色模式自动切换",
    }
}

def get_theme_config(name: str) -> Dict[str, Any]:
    """Retrieve theme configuration with backward compatibility for legacy names."""
    if name in THEMES:
        return THEMES[name]
    if name == "Auto":
        return THEMES["跟随系统 (Auto)"]
    if name == "Dark":
        return THEMES["Fluent 默认深色 (Windows Dark)"]
    if name == "Light":
        return THEMES["Fluent 默认浅色 (Windows Light)"]
    return THEMES["Catppuccin Mocha (猫普钦暗色)"]

def apply_theme(theme_name: str = None, window: Optional[QWidget] = None):
    """Apply theme mode, accent color, and window/sidebar styles."""
    from .settings import settings

    if theme_name is None:
        theme_name = settings.theme_mode

    cfg = get_theme_config(theme_name)

    # 1. Apply theme mode (Light / Dark / Auto)
    setTheme(cfg["mode"])

    # 2. Apply theme accent color
    setThemeColor(cfg["accent"])

    # 3. Apply window and sidebar styling if window instance is provided
    if window:
        wb = cfg.get("window_bg")
        use_mica = cfg.get("use_mica", False)

        if wb and not use_mica:
            window.setMicaEffectEnabled(False)
            window.setCustomBackgroundColor(wb, wb)
            window.setBackgroundColor(QColor(wb))
            
            sb = cfg.get("sidebar_bg", "transparent")
            s_border = cfg.get("sidebar_border", "transparent")
            if sb != "transparent":
                window.navigationInterface.setStyleSheet(
                    f"NavigationInterface {{ background-color: {sb}; border-right: 1px solid {s_border}; }}"
                )
            else:
                window.navigationInterface.setStyleSheet("")
                
            # Stacked widget border
            window.stackedWidget.setStyleSheet(
                f"StackedWidget {{ border: 1px solid {s_border}; border-right: none; border-bottom: none; border-top-left-radius: 10px; background-color: transparent; }}"
            )
        else:
            # Auto / Mica
            window.setMicaEffectEnabled(True)
            window.setCustomBackgroundColor("#F0F4F9", "#202020")
            window.setBackgroundColor(window._normalBackgroundColor())
            window.navigationInterface.setStyleSheet("")
            window.stackedWidget.setStyleSheet("")

        window.update()
