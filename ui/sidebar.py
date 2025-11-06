from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel
from PyQt5.QtCore import pyqtSignal, Qt

class Sidebar(QWidget):
    module_changed = pyqtSignal(str)

    def __init__(self, module_manager):
        super().__init__()
        self.module_manager = module_manager
        self.init_ui()

        # 🔔 коли змінюються модулі — оновлюємо список
        self.module_manager.modules_changed.connect(self.refresh_module_list)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Модулі")
        title.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px;")
        layout.addWidget(title)

        self.module_list = QListWidget()
        self.module_list.setStyleSheet("""
            QListWidget { border: none; font-size: 13px; }
            QListWidget::item { padding: 8px 10px; }
            QListWidget::item:hover { background-color: #f0f0f0; }
            QListWidget::item:selected { background-color: #e0e0e0; color: #000; }
        """)
        layout.addWidget(self.module_list)

        self.module_list.currentTextChanged.connect(self.module_changed.emit)

        # 🧩 початкове заповнення
        self.refresh_module_list()

    def refresh_module_list(self):
        """🔄 Оновлює список активних модулів."""
        current = self.module_list.currentItem().text() if self.module_list.currentItem() else None

        self.module_list.clear()
        for module in self.module_manager.get_all_modules():
            self.module_list.addItem(module.name)

        if current:
            matches = self.module_list.findItems(current, Qt.MatchExactly)
            if matches:
                self.module_list.setCurrentItem(matches[0])
