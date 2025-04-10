from modules.base_module import BaseModule
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QCalendarWidget, 
                            QTextEdit, QPushButton, QLabel, QAction)
from PyQt5.QtCore import QDate, Qt, QLocale
from PyQt5.QtGui import QTextCharFormat, QColor
import json
import os

class CalendarModule(BaseModule):
    def __init__(self):
        super().__init__("Календар", "calendar.png", "Продуктивність")
        self.notes_file = "calendar_notes.json"
        self.notes = self.load_notes()
        self.calendar = None  # Ініціалізуємо як None
    
    def get_menu_actions(self):
        """Реалізація абстрактного методу"""
        self.clear_notes_action = QAction("Очистити всі замітки", self)
        self.clear_notes_action.triggered.connect(self.clear_all_notes)
        return [self.clear_notes_action]
    
    def create_content_widget(self) -> QWidget:
        """Реалізація абстрактного методу"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Український календар (спершу ініціалізуємо)
        self.calendar = QCalendarWidget()
        self.calendar.setLocale(QLocale(QLocale.Ukrainian, QLocale.Ukraine))
        self.calendar.setGridVisible(True)
        
        # Тепер можна застосовувати стилі
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                font-size: 14px;
            }
            QCalendarWidget QToolButton {
                font-size: 16px;
                color: #0055ff;
            }
        """)
        
        # Інші елементи інтерфейсу...
        self.date_label = QLabel()
        self.notes_edit = QTextEdit()
        self.save_btn = QPushButton("Зберегти замітку")
        self.content_widget = QWidget()  # Додаємо збереження віджета як атрибута
    
        
        # Розміщення елементів...
        layout.addWidget(self.date_label)
        layout.addWidget(self.calendar)
        layout.addWidget(self.notes_edit)
        layout.addWidget(self.save_btn)
        layout = QVBoxLayout(self.content_widget)
        
        # Підключення сигналів
        self.calendar.selectionChanged.connect(self.on_date_selected)
        self.save_btn.clicked.connect(self.save_note)
        
        # Завантажуємо виділення для дат з замітками
        self.highlight_dates_with_notes()
        
        return widget
   
    def load_notes(self):
        """Завантажує замітки з файлу"""
        if os.path.exists(self.notes_file):
            with open(self.notes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_notes(self):
        """Зберігає замітки у файл"""
        with open(self.notes_file, 'w', encoding='utf-8') as f:
            json.dump(self.notes, f, ensure_ascii=False, indent=2)
    
    def on_date_selected(self):
        """Обробник вибору дати"""
        selected_date = self.calendar.selectedDate()
        self.update_date_label(selected_date)
        self.show_note_for_date(selected_date)
    
    def update_date_label(self, date):
        """Оновлює мітку з датою"""
        self.date_label.setText(f"Вибрана дата: {date.toString('dd.MM.yyyy')}")
    
    def show_note_for_date(self, date):
        """Показує замітку для вибраної дати"""
        date_str = date.toString("yyyy-MM-dd")
        self.notes_edit.setPlainText(self.notes.get(date_str, ""))
    
    def save_note(self):
        """Зберігає замітку для поточної дати"""
        selected_date = self.calendar.selectedDate()
        date_str = selected_date.toString("yyyy-MM-dd")
        note_text = self.notes_edit.toPlainText()
        
        if note_text.strip():
            self.notes[date_str] = note_text
        elif date_str in self.notes:
            del self.notes[date_str]
        
        self.save_notes()
        self.highlight_dates_with_notes()
        
        from PyQt5.QtWidgets import QMessageBox
        # Змінив self на self.content_widget (або None, якщо content_widget не існує)
        parent_widget = getattr(self, 'content_widget', None)
        QMessageBox.information(
            parent_widget,  # Використовуємо content_widget як батьківський віджет
            "Успіх", 
            "Замітку збережено!" if note_text.strip() else "Замітку видалено"
        )

    def highlight_dates_with_notes(self):

        if self.calendar is None:
            return
        
        """Виділяє дати, для яких є замітки"""
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor(255, 255, 150))  # Жовтий фон
        highlight_format.setFontWeight(75)  # Напівжирний
        
        # Скидаємо попереднє виділення
        for date in self.notes.keys():
            qdate = QDate.fromString(date, "yyyy-MM-dd")
            if qdate.isValid():
                self.calendar.setDateTextFormat(qdate, QTextCharFormat())
        
        # Виділяємо нові дати
        for date in self.notes.keys():
            qdate = QDate.fromString(date, "yyyy-MM-dd")
            if qdate.isValid():
                self.calendar.setDateTextFormat(qdate, highlight_format)