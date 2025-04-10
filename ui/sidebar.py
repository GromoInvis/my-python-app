from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel
from PyQt5.QtCore import pyqtSignal

class Sidebar(QWidget):
    module_changed = pyqtSignal(str)
    
    def __init__(self, module_manager):
        super().__init__()
        self.module_manager = module_manager
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Заголовок
        title = QLabel("Модулі")
        title.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px;")
        layout.addWidget(title)
        
        # Список модулів
        self.module_list = QListWidget()
        self.module_list.setStyleSheet("""
            QListWidget {
                border: none;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 8px 10px;
            }
            QListWidget::item:hover {
                background-color: #f0f0f0;
            }
            QListWidget::item:selected {
                background-color: #e0e0e0;
                color: #000;
            }
        """)
        
        # Додаємо модулі до списку
        for module in self.module_manager.get_all_modules():
            self.module_list.addItem(module.name)
        
        self.module_list.currentTextChanged.connect(self.module_changed.emit)
        layout.addWidget(self.module_list)