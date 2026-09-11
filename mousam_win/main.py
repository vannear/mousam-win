import sys
import os
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from mousam_win.ui.main_window import MainWindow

def main():
    # Configure High DPI scaling for crisp display on 4K/retina monitors
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    app.setApplicationName("Mousam")
    app.setOrganizationName("Mousam")

    from mousam_win.core.theme_manager import apply_theme
    from mousam_win.core.settings import settings
    from mousam_win.core.font_manager import apply_font_settings

    # 1. Apply Theme
    apply_theme()

    # 2. Apply Custom Font Family & Size Scaling
    apply_font_settings()

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
