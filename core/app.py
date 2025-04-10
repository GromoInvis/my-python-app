import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from core.module_manager import ModuleManager

class MyApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.module_manager = ModuleManager()
        self.main_window = MainWindow(self.module_manager)
        
    def run(self):
        self.main_window.show()
        sys.exit(self.app.exec_())