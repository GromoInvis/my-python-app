# modules/base_module.py
from abc import ABC, abstractmethod
from PyQt5.QtWidgets import QWidget

class BaseModule(ABC):
    def __init__(self, name, icon, category="General"):
        self.name = name
        self.icon = icon
        self.category = category
    
    @abstractmethod
    def create_content_widget(self) -> QWidget:
        """Створює віджет з вмістом модуля для головного вікна"""
        pass
    
    @abstractmethod
    def get_menu_actions(self):
        """Повертає дії для додавання у меню програми"""
        return []