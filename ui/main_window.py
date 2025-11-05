from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QHBoxLayout, QWidget
from ui.sidebar import Sidebar
from ui.menu_bar import MenuBar
from ui.styles import LIGHT_THEME, DARK_THEME
from PyQt5.QtGui import QIcon
from core.theme_manager import ThemeManager

class MainWindow(QMainWindow):
    def __init__(self, module_manager):
        super().__init__()
        self.module_manager = module_manager
        self.theme_manager = ThemeManager()  # 🎨 глобальний менеджер теми

        self.setWindowTitle("All in One")
        self.setWindowIcon(QIcon("icons/app_icon.png"))
        self.setGeometry(100, 100, 1000, 600)
        
        # Створюємо елементи UI
        self.menu_bar = MenuBar(self)
        self.sidebar = Sidebar(self.module_manager)
        self.content_stack = QStackedWidget()
        
        self.init_ui()

    def init_ui(self):
        self.setMenuBar(self.menu_bar)
        main_container = QWidget()
        main_layout = QHBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.sidebar.setFixedWidth(200)
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_stack, 1)
        self.setCentralWidget(main_container)
        
        # Підключення сигналів
        self.menu_bar.theme_changed.connect(self.toggle_theme)
        self.sidebar.module_changed.connect(self.change_module)
        self.theme_manager.theme_changed.connect(self.apply_theme_to_all)

        # Застосовуємо поточну тему
        self.apply_theme_to_all(self.theme_manager.current_theme)

        # Встановлюємо перший модуль
        modules = self.module_manager.get_all_modules()
        if modules:
            self.sidebar.module_list.setCurrentRow(0)
            self.change_module(modules[0].name)

    # ──────────────────────────────
    # 🎨 Робота з темою
    # ──────────────────────────────
    def toggle_theme(self):
        self.theme_manager.toggle_theme()

    def apply_theme_to_all(self, theme_name: str):
        theme = DARK_THEME if theme_name == "dark" else LIGHT_THEME
        self.setStyleSheet(theme["MAIN"])
        self.sidebar.setStyleSheet(theme["SIDEBAR"])

        # 🔁 Передаємо всім модулям сигнал зміни теми
        for module in self.module_manager.get_all_modules():
            if hasattr(module, "on_theme_changed"):
                module.on_theme_changed(theme_name)

    # ──────────────────────────────
    # 🔄 Перемикання модулів
    # ──────────────────────────────
    def change_module(self, module_name):
        module = self.module_manager.get_module(module_name)
        if module:
            content_widget = module.create_content_widget()
            self.content_stack.addWidget(content_widget)
            self.content_stack.setCurrentWidget(content_widget)
            self.setWindowTitle(f"All in One - {module.name}")
