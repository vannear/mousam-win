from PyQt5.QtCore import Qt, QTimer, QObject, QEvent, QMimeData
from PyQt5.QtGui import QIcon, QDrag
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import (
    FluentWindow, NavigationItemPosition, FluentIcon, setTheme, Theme
)

from ..core.configs import ASSETS_DIR
from ..core.settings import settings
from ..core.models import Location
from .weather_interface import WeatherInterface
from .city_interface import CityInterface
from .setting_interface import SettingInterface


class CityTabDragFilter(QObject):
    """Event filter attached to city navigation items enabling drag-and-drop reordering."""

    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.drag_start_pos = None

    def eventFilter(self, obj, event):
        etype = event.type()
        if etype == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                self.drag_start_pos = event.pos()
        elif etype == QEvent.MouseMove:
            if self.drag_start_pos and (event.buttons() & Qt.LeftButton):
                if (event.pos() - self.drag_start_pos).manhattanLength() >= QApplication.startDragDistance():
                    city_name = obj.property('cityName')
                    if city_name:
                        drag = QDrag(obj)
                        mime = QMimeData()
                        mime.setText(f"mousam_city:{city_name}")
                        drag.setMimeData(mime)
                        drag.setPixmap(obj.grab())
                        drag.setHotSpot(event.pos())
                        self.drag_start_pos = None
                        drag.exec_(Qt.MoveAction)
                        return True
        elif etype == QEvent.MouseButtonRelease:
            self.drag_start_pos = None
        elif etype == QEvent.DragEnter:
            if event.mimeData().hasText() and event.mimeData().text().startswith("mousam_city:"):
                event.acceptProposedAction()
                return True
        elif etype == QEvent.DragMove:
            if event.mimeData().hasText() and event.mimeData().text().startswith("mousam_city:"):
                event.acceptProposedAction()
                return True
        elif etype == QEvent.Drop:
            if event.mimeData().hasText() and event.mimeData().text().startswith("mousam_city:"):
                src_city = event.mimeData().text().split(":", 1)[1]
                tgt_city = obj.property("cityName")
                if src_city and tgt_city and src_city != tgt_city:
                    self.main_window._reorder_cities(src_city, tgt_city)
                event.acceptProposedAction()
                return True

        return super().eventFilter(obj, event)


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
        self.drag_filter = CityTabDragFilter(self)
        self._build_city_tabs()

        self.addSubInterface(
            self.settingInterface,
            FluentIcon.SETTING,
            "偏好设置",
            NavigationItemPosition.BOTTOM
        )

        self.navigationInterface.setExpandWidth(180)

    def _build_city_tabs(self):
        # Determine currently selected city before rebuilding
        current_route = getattr(self.navigationInterface.panel, '_currentRouteKey', None)
        active_city_name = None
        for w in self.city_widgets:
            if w.objectName() == current_route:
                active_city_name = w.location.name
                break

        # Cache existing WeatherInterface instances by city name
        existing_interfaces = {w.location.name: w for w in self.city_widgets}

        # Cleanly remove city navigation items from layout
        for w in self.city_widgets:
            route_key = w.objectName()
            try:
                nav_item = self.navigationInterface.widget(route_key)
                self.navigationInterface.removeWidget(route_key)
                self.navigationInterface.panel.topLayout.removeWidget(nav_item)
                nav_item.setParent(None)
            except Exception:
                pass

        # Temporarily remove cityInterface navigation item so it stays at the end of the top group
        if hasattr(self, 'cityInterface'):
            try:
                city_key = self.cityInterface.objectName()
                nav_city = self.navigationInterface.widget(city_key)
                self.navigationInterface.removeWidget(city_key)
                self.navigationInterface.panel.topLayout.removeWidget(nav_city)
                nav_city.setParent(None)
            except Exception:
                pass

        self.city_widgets.clear()

        # Delete any cached WeatherInterface that is no longer saved
        saved = settings.saved_cities[:7]
        saved_names = {c.name for c in saved}
        for name, w in list(existing_interfaces.items()):
            if name not in saved_names:
                self.stackedWidget.removeWidget(w)
                w.deleteLater()
                del existing_interfaces[name]

        # Add tabs in the configured order
        target_w = None
        for i, loc in enumerate(saved):
            if loc.name in existing_interfaces:
                w = existing_interfaces[loc.name]
            else:
                w = WeatherInterface(location=loc, parent=self)
                w.request_city_switch.connect(lambda: self.switchTo(self.cityInterface))
                QTimer.singleShot(150 + i * 100, w.load_weather)

            self.addSubInterface(w, FluentIcon.CLOUD, loc.name, position=NavigationItemPosition.TOP)
            self.city_widgets.append(w)

            # Setup drag-and-drop & context menu on navigation item
            nav_item = self.navigationInterface.widget(w.objectName())
            if nav_item:
                nav_item.setProperty("cityName", loc.name)
                nav_item.setAcceptDrops(True)
                nav_item.installEventFilter(self.drag_filter)
                nav_item.setContextMenuPolicy(Qt.CustomContextMenu)
                nav_item.customContextMenuRequested.connect(
                    lambda pos, loc=loc, item=nav_item: self._show_city_context_menu(pos, loc, item)
                )

            if active_city_name and loc.name == active_city_name:
                target_w = w

        # Re-add City Management interface
        if hasattr(self, 'cityInterface'):
            self.addSubInterface(
                self.cityInterface,
                FluentIcon.GLOBE,
                "添加/管理城市",
                position=NavigationItemPosition.TOP
            )

        # Switch to the preserved or first city tab
        if target_w:
            self.switchTo(target_w)
        elif self.city_widgets:
            self.switchTo(self.city_widgets[0])

    def _reorder_cities(self, src_name: str, tgt_name: str):
        saved = settings.saved_cities
        src_idx = next((i for i, c in enumerate(saved) if c.name == src_name), -1)
        tgt_idx = next((i for i, c in enumerate(saved) if c.name == tgt_name), -1)
        if src_idx != -1 and tgt_idx != -1 and src_idx != tgt_idx:
            item = saved.pop(src_idx)
            saved.insert(tgt_idx, item)
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
