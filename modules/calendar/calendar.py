from modules.base_module import BaseModule
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCalendarWidget
from PyQt5.QtCore import QDate

class CalendarModule(BaseModule):
    def __init__(self):
        super().__init__("Календар", "calendar.png", "Продуктивність")
        
    def create_content_widget(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setSelectedDate(QDate.currentDate())
        
        layout.addWidget(self.calendar)
        return widget
    
    def get_menu_actions(self):
        # Повертає дії для меню
        return []