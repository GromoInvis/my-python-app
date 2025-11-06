# ui/module_manager_dialog.py
import os
# import json # ❌ ВИДАЛЕНО: Не використовується
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt

# ❌ ВИДАЛЕНО: Ця константа не використовувалась і дублювала ту, що в менеджері
# MODULE_STATE_FILE = "config/module_state.json" 


class ModuleManagerDialog(QDialog):
    """Вікно для керування модулями (увімкнути / вимкнути / оновити)."""

    def __init__(self, module_manager, sidebar=None):
        super().__init__()
        self.setWindowTitle("Керування модулями")
        self.resize(400, 500)

        self.module_manager = module_manager
        self.sidebar = sidebar # Зберігаємо сайдбар, але не оновлюємо його звідси

        self.layout = QVBoxLayout(self)

        # 📋 Список модулів
        self.module_list = QListWidget()
        self.layout.addWidget(self.module_list)

        # 🔘 Кнопки
        btn_layout = QHBoxLayout()
        self.btn_enable = QPushButton("Увімкнути")
        self.btn_disable = QPushButton("Вимкнути")
        self.btn_close = QPushButton("Закрити")

        btn_layout.addWidget(self.btn_enable)
        btn_layout.addWidget(self.btn_disable)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_close)

        self.layout.addLayout(btn_layout)

        # ⚙️ З’єднання подій
        self.btn_enable.clicked.connect(self.enable_module)
        self.btn_disable.clicked.connect(self.disable_module)
        self.btn_close.clicked.connect(self.close)

        # 🔄 Завантажуємо список
        self.load_module_list()

    # ──────────────────────────────
    # 📋 Заповнення списку
    # ──────────────────────────────
    def load_module_list(self):
        """Показує всі модулі із позначками (увімкнено/вимкнено)."""
        self.module_list.clear()
        
        # ✅ Коректно бере стан з менеджера
        state = self.module_manager._load_enabled_state() 

        for folder in os.listdir("modules"):
            if folder in ["__pycache__", "base_module"] or not os.path.isdir(os.path.join("modules", folder)):
                continue

            item = QListWidgetItem(folder)
            item.setCheckState(Qt.Checked if state.get(folder, True) else Qt.Unchecked)
            self.module_list.addItem(item)

    # ──────────────────────────────
    # ✅ Увімкнути
    # ──────────────────────────────
    def enable_module(self):
        current_item = self.module_list.currentItem()
        if not current_item:
            return

        module_name = current_item.text()
        current_item.setCheckState(Qt.Checked)

        self.module_manager.set_module_enabled(module_name, True)
        
        # ❌ ВИДАЛЕНО: self.module_manager.load_modules()
        # ❌ ВИДАЛЕНО: if self.sidebar: self.sidebar.refresh_module_list()

        # ✅ Оновлено повідомлення, щоб попередити користувача
        QMessageBox.information(self, "✅", 
                                f"Модуль '{module_name}' увімкнено!\n\n"
                                "Зміни набудуть чинності після закриття цього вікна.")

    # ──────────────────────────────
    # ⛔ Вимкнути
    # ──────────────────────────────
    def disable_module(self):
        current_item = self.module_list.currentItem()
        if not current_item:
            return

        module_name = current_item.text()
        current_item.setCheckState(Qt.Unchecked)

        self.module_manager.set_module_enabled(module_name, False)
        
        # ❌ ВИДАЛЕНО: self.module_manager.load_modules()
        # ❌ ВИДАЛЕНО: if self.sidebar: self.sidebar.refresh_module_list()

        # ✅ Оновлено повідомлення
        QMessageBox.information(self, "🛑", 
                                f"Модуль '{module_name}' вимкнено!\n\n"
                                "Зміни набудуть чинності після закриття цього вікна.")