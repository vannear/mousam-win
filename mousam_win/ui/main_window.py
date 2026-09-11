from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from qfluentwidgets import (
    FluentWindow, NavigationItemPosition, FluentIcon, setTheme, Theme
)

from ..core.configs import ASSETS_DIR
from ..core.settings import settings
from ..core.models import Location
from .weather_interface import WeatherInterface
from .city_interface import CityInterface
from .setting_interface import SettingInterface

class MainWindow(FluentWindow):
    """Main application window with Fluent sidebar and modern cards."""

    def __init__(self):
        super().__init__()
        self.init_window()
        self.init_navigation()

        # Auto refresh timer
        self.auto_refresh_timer = QTimer(self)
        self.auto_refresh_timer.timeout.connect(self._auto_refresh_all)
        self._setup_auto_refresh()

    def _auto_refresh_all(self):
        for w in getattr(self, 'city_widgets', []):
            w.refresh()

    def init_window(self):
        self.setWindowTitle("Mousam Weather · 天气")
        self.resize(1020, 760)
        self.setMinimumSize(880, 600)

        # Set Window Icon
        icon_path = ASSETS_DIR / "icons" / "apps" / "io.github.amit9838.mousam.svg"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # Apply Theme
        from ..core.theme_manager import apply_theme
        apply_theme(settings.theme_mode, window=self)

    def init_navigation(self):
        self.cityInterface = CityInterface(self)
        self.settingInterface = SettingInterface(self)

        # Connect navigation signals
        self.cityInterface.city_changed.connect(self._on_city_changed)
        self.settingInterface.settings_changed.connect(self._on_settings_changed)

        self.city_widgets = []
        self._build_city_tabs()

        self.addSubInterface(
            self.cityInterface,
            FluentIcon.GLOBE,
            "添加/管理城市"
        )
        self.addSubInterface(
            self.settingInterface,
            FluentIcon.SETTING,
            "偏好设置",
            NavigationItemPosition.BOTTOM
        )

        self.navigationInterface.setExpandWidth(180)

    def _build_city_tabs(self):
        # Remove old tabs
        for w in self.city_widgets:
            self.navigationInterface.removeWidget(w.objectName())
            self.stackedWidget.removeWidget(w)
            w.deleteLater()
        self.city_widgets.clear()

        # Add new tabs for saved cities
        saved = settings.saved_cities[:7]
        for i, loc in enumerate(saved):
            w = WeatherInterface(location=loc, parent=self)
            w.request_city_switch.connect(lambda: self.switchTo(self.cityInterface))
            # Insert at the beginning (before City Management)
            self.addSubInterface(w, FluentIcon.CLOUD, loc.name, position=NavigationItemPosition.TOP)
            self.city_widgets.append(w)
            
            # Setup context menu for the navigation item
            nav_item = self.navigationInterface.widget(w.objectName())
            if nav_item:
                nav_item.setContextMenuPolicy(Qt.CustomContextMenu)
                # Capture loc and nav_item via default arguments
                nav_item.customContextMenuRequested.connect(
                    lambda pos, loc=loc, item=nav_item: self._show_city_context_menu(pos, loc, item)
                )

            # Load weather slightly delayed
            QTimer.singleShot(150 + i * 100, w.load_weather)
            
        # Switch to the first city or selected_city if found
        if self.city_widgets:
            target_w = self.city_widgets[0]
            for w in self.city_widgets:
                if w.location.name == settings.selected_city.name:
                    target_w = w
                    break
            self.switchTo(target_w)

    def _show_city_context_menu(self, pos, loc: Location, nav_item):
        from qfluentwidgets import RoundMenu, Action
        
        menu = RoundMenu(parent=self)
        
        # Determine the index of the current city
        saved = settings.saved_cities
        idx = next((i for i, c in enumerate(saved) if c.name == loc.name), -1)
        
        if idx > 0:
            action_up = Action(FluentIcon.UP, '上移', self)
            action_up.triggered.connect(lambda: self._move_city(idx, -1))
            menu.addAction(action_up)
            
        if idx >= 0 and idx < len(saved) - 1:
            action_down = Action(FluentIcon.DOWN, '下移', self)
            action_down.triggered.connect(lambda: self._move_city(idx, 1))
            menu.addAction(action_down)
            
        if idx >= 0 and len(saved) > 1:
            menu.addSeparator()

        action_delete = Action(FluentIcon.DELETE, '删除此城市', self)
        action_delete.triggered.connect(lambda: self._delete_city_from_sidebar(loc))
        menu.addAction(action_delete)
        
        # Determine global position
        global_pos = nav_item.mapToGlobal(pos)
        menu.exec_(global_pos)

    def _move_city(self, idx: int, direction: int):
        saved = settings.saved_cities
        new_idx = idx + direction
        if 0 <= new_idx < len(saved):
            # Swap
            saved[idx], saved[new_idx] = saved[new_idx], saved[idx]
            # Save manually since we bypassed settings logic
            settings.data["saved_cities"] = [
                {
                    "name": c.name,
                    "country": c.country,
                    "state": c.state,
                    "latitude": c.latitude,
                    "longitude": c.longitude,
                    "timezone": c.timezone,
                } for c in saved
            ]
            settings.save()
            self._build_city_tabs()

    def _delete_city_from_sidebar(self, loc: Location):
        saved = settings.saved_cities
        for i, c in enumerate(saved):
            if abs(c.latitude - loc.latitude) < 0.01 and abs(c.longitude - loc.longitude) < 0.01:
                settings.remove_saved_city(i)
                # Check if we need to switch selected_city
                if settings.selected_city.name == loc.name and settings.saved_cities:
                    settings.selected_city = settings.saved_cities[0]
                break
        self._build_city_tabs()

    def _on_city_changed(self, loc: Location):
        self._build_city_tabs()

    def _on_settings_changed(self):
        self._setup_auto_refresh()
        for w in self.city_widgets:
            w.refresh()

    def _setup_auto_refresh(self):
        interval = settings.data.get("auto_refresh_minutes", 30)
        if interval > 0:
            self.auto_refresh_timer.start(interval * 60 * 1000)
        else:
            self.auto_refresh_timer.stop()
