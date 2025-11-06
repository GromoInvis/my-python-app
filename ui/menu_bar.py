from PyQt5.QtWidgets import QMenuBar, QMenu, QAction
from PyQt5.QtCore import pyqtSignal
from ui.module_manager_dialog import ModuleManagerDialog


class MenuBar(QMenuBar):
    theme_changed = pyqtSignal()
    modules_updated = pyqtSignal()  # 🔥 сигнал про зміну модулів

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # Файл
        file_menu = QMenu("Файл", self)
        exit_action = QAction("Вихід", self)
        exit_action.triggered.connect(self.parent().close)
        file_menu.addAction(exit_action)
        self.addMenu(file_menu)

        # Налаштування
        settings_menu = QMenu("Налаштування", self)
        theme_action = QAction("🌓 Змінити тему", self)
        theme_action.triggered.connect(self.theme_changed.emit)
        settings_menu.addAction(theme_action)
        self.addMenu(settings_menu)

        # 🧩 Меню "Модулі"
        modules_menu = QMenu("Модулі", self)
        manage_modules_action = QAction("Переглянути підключені модулі", self)
        manage_modules_action.triggered.connect(self.open_module_manager)
        modules_menu.addAction(manage_modules_action)
        self.addMenu(modules_menu)

        # Довідка
        help_menu = QMenu("Довідка", self)
        about_action = QAction("Про програму", self)
        about_action.triggered.connect(lambda: print("ℹ️ Про програму — All in One"))
        help_menu.addAction(about_action)
        self.addMenu(help_menu)

    # ──────────────────────────────
    # 🧩 Менеджер модулів
    # ──────────────────────────────
    def open_module_manager(self):
        """Відкрити вікно керування модулями"""
        main_window = self.parent()
        if not main_window or not hasattr(main_window, "module_manager"):
            print("⚠️ Неможливо відкрити менеджер модулів: немає головного вікна або менеджера модулів.")
            return

        dlg = ModuleManagerDialog(main_window.module_manager, main_window.sidebar)
        dlg.exec_()

        # 🔥 після закриття — повідомляємо головне вікно
        self.modules_updated.emit()
