from PyQt5.QtWidgets import QMenuBar, QMenu, QAction
from PyQt5.QtCore import pyqtSignal

class MenuBar(QMenuBar):
    theme_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        file_menu = QMenu("Файл", self)
        exit_action = QAction("Вихід", self)
        exit_action.triggered.connect(self.parent().close)
        file_menu.addAction(exit_action)
        self.addMenu(file_menu)
        
        settings_menu = QMenu("Налаштування", self)
        theme_action = QAction("🌓 Змінити тему", self)
        theme_action.triggered.connect(self.theme_changed.emit)
        settings_menu.addAction(theme_action)
        self.addMenu(settings_menu)
        
        help_menu = QMenu("Довідка", self)
        about_action = QAction("Про програму", self)
        about_action.triggered.connect(lambda: print("ℹ️ Про програму — All in One"))
        help_menu.addAction(about_action)
        self.addMenu(help_menu)
