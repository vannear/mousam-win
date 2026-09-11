from typing import List
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from qfluentwidgets import (
    TitleLabel, SubtitleLabel, StrongBodyLabel, BodyLabel, CaptionLabel,
    SearchLineEdit, CardWidget, PushButton, PrimaryPushButton, ToolButton,
    FluentIcon, InfoBar, InfoBarPosition, SmoothScrollArea
)
from ..core.models import Location
from ..core.settings import settings
from ..core.api import search_cities

class CityCard(CardWidget):
    """Card representing a saved or searched city."""

    selected = pyqtSignal(Location)
    deleted = pyqtSignal(Location)

    def __init__(self, location: Location, is_saved: bool = True, parent=None):
        super().__init__(parent)
        self.location = location
        self.is_saved = is_saved
        self.setFixedHeight(72)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(16)

        # Icon
        icon_lbl = QLabel("📍", self)
        f = icon_lbl.font()
        f.setPointSize(16)
        icon_lbl.setFont(f)
        layout.addWidget(icon_lbl)

        # City info
        info_box = QVBoxLayout()
        info_box.setSpacing(2)
        lbl_name = StrongBodyLabel(location.name, self)
        info_box.addWidget(lbl_name)

        lbl_sub = CaptionLabel(location.display_name, self)
        info_box.addWidget(lbl_sub)
        layout.addLayout(info_box, 1)

        # Actions
        btn_text = "查看天气面板" if is_saved else "添加至侧边栏"
        self.btn_select = PrimaryPushButton(btn_text, self)
        self.btn_select.setFixedWidth(120)
        self.btn_select.clicked.connect(lambda: self.selected.emit(self.location))
        layout.addWidget(self.btn_select)

        if is_saved:
            self.btn_delete = ToolButton(FluentIcon.DELETE, self)
            self.btn_delete.setToolTip("从收藏中移除")
            self.btn_delete.clicked.connect(lambda: self.deleted.emit(self.location))
            layout.addWidget(self.btn_delete)


class CityInterface(QWidget):
    """City management interface with search and favorites list."""

    city_changed = pyqtSignal(Location)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("cityInterface")
        self.search_results: List[Location] = []

        self.init_ui()
        self.load_saved_cities()

        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(400)
        self.search_timer.timeout.connect(self._do_search)

    def init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(36, 24, 36, 24)
        root_layout.setSpacing(20)

        # 1. Header
        header_box = QVBoxLayout()
        header_box.setSpacing(4)
        title = TitleLabel("城市管理", self)
        header_box.addWidget(title)

        subtitle = CaptionLabel("实时搜索全球城市，或快速切换和管理您的常用城市", self)
        header_box.addWidget(subtitle)
        root_layout.addLayout(header_box)

        # 2. Search Box
        self.search_bar = SearchLineEdit(self)
        self.search_bar.setPlaceholderText("输入中文或英文城市名（例如：成都、杭州、Tokyo、London）...")
        self.search_bar.textChanged.connect(self._on_search_changed)
        self.search_bar.searchSignal.connect(self._do_search)
        root_layout.addWidget(self.search_bar)

        # Scroll Area for lists
        self.scroll = SmoothScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("background: transparent;")

        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(16)

        # Search Results Container
        self.results_title = StrongBodyLabel("搜索结果", self)
        self.results_title.hide()
        self.content_layout.addWidget(self.results_title)

        self.results_layout = QVBoxLayout()
        self.results_layout.setSpacing(8)
        self.content_layout.addLayout(self.results_layout)

        # Saved Cities Container
        self.saved_title = StrongBodyLabel("已收藏城市", self)
        self.content_layout.addWidget(self.saved_title)

        self.saved_layout = QVBoxLayout()
        self.saved_layout.setSpacing(8)
        self.content_layout.addLayout(self.saved_layout)

        self.content_layout.addStretch()
        self.scroll.setWidget(self.content_widget)
        root_layout.addWidget(self.scroll, 1)

    def load_saved_cities(self):
        # Clear existing
        while self.saved_layout.count():
            item = self.saved_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        saved = settings.saved_cities
        for loc in saved:
            card = CityCard(loc, is_saved=True, parent=self.content_widget)
            card.selected.connect(self._on_city_selected)
            card.deleted.connect(self._on_city_deleted)
            self.saved_layout.addWidget(card)

    def _on_search_changed(self, text: str):
        if not text.strip():
            self.results_title.hide()
            while self.results_layout.count():
                item = self.results_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            self.search_timer.stop()
            return
        self.search_timer.start()

    def _do_search(self):
        query = self.search_bar.text().strip()
        if not query:
            return

        # Clear previous results
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        results = search_cities(query, count=6)
        if results:
            self.results_title.setText(f"搜索结果 ({len(results)})")
            self.results_title.show()
            for loc in results:
                card = CityCard(loc, is_saved=False, parent=self.content_widget)
                card.selected.connect(self._on_search_city_selected)
                self.results_layout.addWidget(card)
        else:
            self.results_title.setText("未找到相关城市")
            self.results_title.show()

    def _on_search_city_selected(self, loc: Location):
        if len(settings.saved_cities) >= 7:
            InfoBar.warning(
                title="已达到上限",
                content="最多只能收藏 7 个城市，请先删除部分常用城市",
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000,
                parent=self.window()
            )
            return

        settings.add_saved_city(loc)
        settings.selected_city = loc
        self.load_saved_cities()
        self.city_changed.emit(loc)
        InfoBar.success(
            title="添加成功",
            content=f"已将 {loc.display_name} 添加到侧边栏",
            position=InfoBarPosition.TOP_RIGHT,
            duration=3000,
            parent=self.window()
        )

    def _on_city_selected(self, loc: Location):
        settings.selected_city = loc
        self.city_changed.emit(loc)
        InfoBar.success(
            title="跳转成功",
            content=f"已跳转至 {loc.display_name} 的天气面板",
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000,
            parent=self.window()
        )

    def _on_city_deleted(self, loc: Location):
        saved = settings.saved_cities
        for i, c in enumerate(saved):
            if abs(c.latitude - loc.latitude) < 0.01 and abs(c.longitude - loc.longitude) < 0.01:
                settings.remove_saved_city(i)
                break
        self.load_saved_cities()
        InfoBar.info(
            title="已移除",
            content=f"已从常用列表中移除 {loc.name}",
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000,
            parent=self.window()
        )
