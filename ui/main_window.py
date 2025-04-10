from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QHBoxLayout, QWidget
from ui.sidebar import Sidebar
from ui.menu_bar import MenuBar
from PyQt5.QtGui import QIcon

class MainWindow(QMainWindow):
    def __init__(self, module_manager):
        super().__init__()
        self.module_manager = module_manager
        self.current_module = None
        
        self.setWindowTitle("All in One")
        self.setWindowIcon(QIcon("icons/app_icon.png"))
        self.setGeometry(100, 100, 1000, 600)
        
        # Спочатку створюємо всі віджети
        self.menu_bar = MenuBar(self)
        self.sidebar = Sidebar(self.module_manager)  # Створюємо sidebar тут
        self.content_stack = QStackedWidget()
        
        # Потім ініціалізуємо UI
        self.init_ui()
    
    def init_ui(self):
        # Встановлюємо верхнє меню
        self.setMenuBar(self.menu_bar)
        
        # Головний контейнер
        main_container = QWidget()
        main_layout = QHBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Налаштування бічної панелі
        self.sidebar.setFixedWidth(200)
        main_layout.addWidget(self.sidebar)
        
        # Область контенту
        main_layout.addWidget(self.content_stack, 1)
        
        self.setCentralWidget(main_container)
        
        # Підключення сигналів
        self.sidebar.module_changed.connect(self.change_module)
        
        # Встановлення стилів
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
        """)
        
        self.sidebar.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-right: 1px solid #dee2e6;
            }
        """)
        
        # Встановлення першого модуля
        if self.module_manager.get_all_modules():
            first_module = self.module_manager.get_all_modules()[0].name
            self.sidebar.module_list.setCurrentRow(0)
            self.change_module(first_module)
    
    def change_module(self, module_name):
        module = self.module_manager.get_module(module_name)
        if module:
            self.current_module = module
            content_widget = module.create_content_widget()
            
            # Видаляємо попередній віджет, якщо він існує
            for i in range(self.content_stack.count()):
                if self.content_stack.widget(i).__class__ == content_widget.__class__:
                    self.content_stack.removeWidget(self.content_stack.widget(i))
                    break
            
            self.content_stack.addWidget(content_widget)
            self.content_stack.setCurrentWidget(content_widget)
            self.setWindowTitle(f"All in One - {module.name}")