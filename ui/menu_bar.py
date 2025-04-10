from PyQt5.QtWidgets import QMenuBar, QMenu, QAction

class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        # Меню Файл
        file_menu = QMenu("Файл", self)
        
        exit_action = QAction("Вихід", self)
        exit_action.triggered.connect(self.parent().close)
        
        file_menu.addAction(exit_action)
        self.addMenu(file_menu)
        
        # Меню Налаштування
        settings_menu = QMenu("Налаштування", self)
        self.addMenu(settings_menu)