from typing import List, Optional
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidgetItem, QLabel
)
from qfluentwidgets import (
    MessageBoxBase, SubtitleLabel, StrongBodyLabel, BodyLabel, CaptionLabel,
    SearchLineEdit, ListWidget, PushButton, ToolButton, FluentIcon
)
from ..core.models import Location
from ..core.settings import settings
from ..core.api import search_cities

class CitySearchDialog(MessageBoxBase):
    """Fluent dialog for searching and switching cities."""

    city_selected = pyqtSignal(Location)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_location: Optional[Location] = None
        self.search_results: List[Location] = []

        self.init_ui()
        self.load_saved_cities()

        # Debounce timer for search
        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(400)
        self.search_timer.timeout.connect(self._do_search)

    def init_ui(self):
        self.titleLabel = SubtitleLabel("城市管理与搜索", self)
        self.viewLayout.addWidget(self.titleLabel)

        # 1. Search Bar
        self.search_bar = SearchLineEdit(self)
        self.search_bar.setPlaceholderText("输入城市名称（如：北京、东京、London、Paris）...")
        self.search_bar.textChanged.connect(self._on_search_text_changed)
        self.search_bar.searchSignal.connect(self._do_search)
        self.viewLayout.addWidget(self.search_bar)

        # 2. Search Results
        self.lbl_results = StrongBodyLabel("搜索结果", self)
        self.lbl_results.hide()
        self.viewLayout.addWidget(self.lbl_results)

        self.list_results = ListWidget(self)
        self.list_results.setFixedHeight(120)
        self.list_results.hide()
        self.list_results.itemClicked.connect(self._on_result_clicked)
        self.viewLayout.addWidget(self.list_results)

        # 3. Saved Cities
        self.lbl_saved = StrongBodyLabel("已保存城市", self)
        self.viewLayout.addWidget(self.lbl_saved)

        self.list_saved = ListWidget(self)
        self.list_saved.setFixedHeight(150)
        self.list_saved.itemClicked.connect(self._on_saved_clicked)
        self.viewLayout.addWidget(self.list_saved)

        self.widget.setMinimumWidth(440)
        self.yesButton.setText("确定")
        self.cancelButton.setText("取消")

    def load_saved_cities(self):
        self.list_saved.clear()
        saved = settings.saved_cities
        for loc in saved:
            item = QListWidgetItem(f"📍 {loc.display_name}")
            item.setData(Qt.UserRole, loc)
            self.list_saved.addItem(item)

    def _on_search_text_changed(self, text: str):
        if not text.strip():
            self.lbl_results.hide()
            self.list_results.hide()
            self.list_results.clear()
            self.search_timer.stop()
            return
        self.search_timer.start()

    def _do_search(self):
        query = self.search_bar.text().strip()
        if not query:
            return

        self.list_results.clear()
        results = search_cities(query, count=6)
        self.search_results = results

        if results:
            self.lbl_results.setText(f"搜索结果 ({len(results)})")
            self.lbl_results.show()
            self.list_results.show()

            for loc in results:
                item = QListWidgetItem(f"🔍 {loc.display_name} (经度: {round(loc.longitude, 2)}, 纬度: {round(loc.latitude, 2)})")
                item.setData(Qt.UserRole, loc)
                self.list_results.addItem(item)
        else:
            self.lbl_results.setText("未找到相关城市")
            self.lbl_results.show()
            self.list_results.hide()

    def _on_result_clicked(self, item: QListWidgetItem):
        loc = item.data(Qt.UserRole)
        if loc:
            self.selected_location = loc
            settings.add_saved_city(loc)
            settings.selected_city = loc
            self.city_selected.emit(loc)
            self.accept()

    def _on_saved_clicked(self, item: QListWidgetItem):
        loc = item.data(Qt.UserRole)
        if loc:
            self.selected_location = loc
            settings.selected_city = loc
            self.city_selected.emit(loc)
            self.accept()
