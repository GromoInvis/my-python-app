# main_window.py (Повністю оновлена версія)

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
        self.theme_manager = ThemeManager()

        self.setWindowTitle("All in One")
        self.setWindowIcon(QIcon("icons/app_icon.png"))
        self.setGeometry(100, 100, 1000, 600)
        
        # 🧩 UI компоненти
        self.menu_bar = MenuBar(self)
        self.sidebar = Sidebar(self.module_manager)
        self.content_stack = QStackedWidget()
        self.menu_bar.modules_updated.connect(self.reload_modules)

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
        
        # 🔗 Сигнали
        self.menu_bar.theme_changed.connect(self.toggle_theme)
        self.menu_bar.modules_updated.connect(self.reload_modules)
        self.sidebar.module_changed.connect(self.change_module)
        self.theme_manager.theme_changed.connect(self.apply_theme_to_all)
        self.module_manager.modules_changed.connect(self.refresh_sidebar)


        # 🎨 Тема
        self.apply_theme_to_all(self.theme_manager.current_theme)

        # 🧱 Початковий модуль
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

        # 🔁 Передаємо зміну теми всім модулям
        for module in self.module_manager.get_all_modules():
            if hasattr(module, "on_theme_changed"):
                module.on_theme_changed(theme_name)

    # ──────────────────────────────
    # 🧩 Перемикання та оновлення модулів (ОНОВЛЕНО)
    # ──────────────────────────────
    def change_module(self, module_name):
        
        # --- НОВИЙ БЛОК 1: Сховати старий модуль ---
        # Викликаємо "on_hide" для поточного модуля, ПЕРЕД перемиканням
        current_widget = self.content_stack.currentWidget()
        if current_widget and hasattr(current_widget, "module_name"):
            old_module_name = current_widget.module_name
            if old_module_name:
                old_module = self.module_manager.get_module(old_module_name)
                if old_module and hasattr(old_module, "on_module_hidden"):
                    print(f"⏸️ Ховаю модуль: {old_module_name}")
                    old_module.on_module_hidden()
        # --- КІНЕЦЬ БЛОКУ 1 ---

        module = self.module_manager.get_module(module_name)
        if not module:
            return

        # 🔍 Якщо цей модуль уже відкритий — просто перемикаємось
        for i in range(self.content_stack.count()):
            w = self.content_stack.widget(i)
            if getattr(w, "module_name", None) == module_name:
                self.content_stack.setCurrentWidget(w)
                self.setWindowTitle(f"All in One - {module.name}")
                
                # --- НОВИЙ БЛОК 2: Показати модуль (що вже існує) ---
                if hasattr(module, "on_module_shown"):
                    print(f"▶️ Повертаю модуль: {module.name}")
                    module.on_module_shown()
                # --- КІНЕЦЬ БЛОКУ 2 ---
                return

        # 🆕 Інакше додаємо новий віджет
        content_widget = module.create_content_widget()
        content_widget.module_name = module_name
        self.content_stack.addWidget(content_widget)
        self.content_stack.setCurrentWidget(content_widget)
        self.setWindowTitle(f"All in One - {module.name}")
        
        # --- НОВИЙ БЛОК 3: Показати модуль (новий) ---
        if hasattr(module, "on_module_shown"):
            print(f"▶️ Показую (вперше) модуль: {module.name}")
            module.on_module_shown()
        # --- КІНЕЦЬ БЛОКУ 3 ---


    def reload_modules(self):
        """🔄 Викликається після зміни активних модулів у менеджері."""
        print("🔁 Оновлення модулів після зміни в менеджері...")

        # --- НОВИЙ БЛОК 1: Очищення старих модулів ---
        # Коректно очищуємо ВСІ старі віджети та їхні модулі
        # Це потрібно зробити ДО того, як ми очистимо self.module_manager.modules
        print(f"🧹 Очищення {self.content_stack.count()} старих віджетів...")
        for i in range(self.content_stack.count()):
            widget = self.content_stack.widget(i)
            if widget and hasattr(widget, "module_name"):
                module = self.module_manager.get_module(widget.module_name)
                if module and hasattr(module, "cleanup_module"):
                    module.cleanup_module()
        # --- КІНЕЦЬ БЛОКУ 1 ---

        # Повторно завантажити модулі
        self.module_manager.modules.clear()
        self.module_manager.load_modules()

        # Оновити Sidebar
        self.sidebar.refresh_module_list()
        
        # --- НОВИЙ БЛОК 2: Очищення стека віджетів ---
        # Тепер видаляємо всі старі віджети зі стека
        while self.content_stack.count() > 0:
            w = self.content_stack.widget(0)
            self.content_stack.removeWidget(w)
            w.deleteLater() # Явно видаляємо віджет
        # --- КІНЕЦЬ БЛОКУ 2 ---

        # Перезавантажити перший активний модуль
        modules = self.module_manager.get_all_modules()
        if modules:
            self.sidebar.module_list.setCurrentRow(0)
            self.change_module(modules[0].name)
        else:
            # Якщо модулів не лишилось, очищуємо сайдбар
            self.sidebar.module_list.clear()

    def refresh_sidebar(self):
        """Оновлює список модулів у сайдбарі при зміні стану модулів"""
        self.sidebar.refresh_module_list()