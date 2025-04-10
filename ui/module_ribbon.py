from PyQt5.QtWidgets import QToolBar, QAction
from PyQt5.QtCore import pyqtSignal

class ModuleRibbon(QToolBar):
    module_changed = pyqtSignal(str)
    
    def __init__(self, module_manager, parent=None):
        super().__init__("Модулі", parent)
        self.module_manager = module_manager
        self.init_ui()
    
    def init_ui(self):
        self.setMovable(False)
        
        for module in self.module_manager.get_all_modules():
            action = QAction(module.name, self)
            action.setData(module.name)
            action.triggered.connect(lambda _, name=module.name: self.module_changed.emit(name))
            self.addAction(action)