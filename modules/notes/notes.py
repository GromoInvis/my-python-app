from modules.base_module import BaseModule
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QToolBar, 
                            QAction, QMessageBox, QColorDialog, QApplication, QActionGroup, QFileDialog)
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QFont, QTextBlockFormat, QIcon
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
import os

class NotesModule(BaseModule):
    def __init__(self):
        super().__init__("Блокнот+", "notes.png", "Продуктивність")
        self.file_path = os.path.join("data", "notes_data.html")  # Шлях до єдиного файлу
        os.makedirs("data", exist_ok=True)  # Створюємо папку, якщо немає
        self.setup_auto_save()
        self.current_color = None

    def create_content_widget(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Текстове поле з підтримкою HTML
        self.text_edit = QTextEdit()
        self.text_edit.setAcceptRichText(True)
        
        # Панель інструментів
        self.toolbar = QToolBar()
        self.setup_toolbar()
        
        layout.addWidget(self.toolbar)
        layout.addWidget(self.text_edit)
        
        self.load_content()  # Завантажуємо вміст при старті
        return widget
    
    def setup_toolbar(self):
        """Налаштування панелі інструментів з кнопками вирівнювання"""
        # Кнопки форматування тексту
        bold_action = QAction(QIcon("icons/bold.png"), "Жирний", self.text_edit)
        bold_action.triggered.connect(self.toggle_bold)
        
        italic_action = QAction(QIcon("icons/italic.png"), "Курсив", self.text_edit)
        italic_action.triggered.connect(self.toggle_italic)
        
        color_action = QAction(QIcon("icons/color.png"), "Колір", self.text_edit)
        color_action.triggered.connect(self.change_color)
        
        date_action = QAction(QIcon("icons/date.png"), "Дата", self.text_edit)
        date_action.triggered.connect(self.insert_date)

        # Група кнопок вирівнювання
        align_group = QActionGroup(self.text_edit)
        align_left = QAction(QIcon("icons/align_left.png"), "Ліворуч (Ctrl+L)", align_group)
        align_left.setCheckable(True)
        align_left.setShortcut("Ctrl+L")
        align_left.triggered.connect(lambda: self.set_alignment(Qt.AlignLeft))
        
        align_center = QAction(QIcon("icons/align_center.png"), "По центру (Ctrl+E)", align_group)
        align_center.setCheckable(True)
        align_center.setShortcut("Ctrl+E")
        align_center.triggered.connect(lambda: self.set_alignment(Qt.AlignCenter))
        
        align_right = QAction(QIcon("icons/align_right.png"), "Праворуч (Ctrl+R)", align_group)
        align_right.setCheckable(True)
        align_right.setShortcut("Ctrl+R")
        align_right.triggered.connect(lambda: self.set_alignment(Qt.AlignRight))

        # Кнопка збереження
        save_action = QAction(QIcon("icons/save.png"), "Зберегти", self.text_edit)
        save_action.triggered.connect(self.force_save)

        # Додаємо всі кнопки на панель
        self.toolbar.addAction(bold_action)
        self.toolbar.addAction(italic_action)
        self.toolbar.addAction(color_action)
        self.toolbar.addSeparator()
        self.toolbar.addActions(align_group.actions())
        self.toolbar.addSeparator()
        self.toolbar.addAction(date_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(save_action)

    def setup_auto_save(self):
        """Налаштування автозбереження"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.save_content)
        self.timer.start(2000)  # Зберігає кожні 2 секунд

    def set_alignment(self, alignment):
        """Зміна вирівнювання виділеного тексту"""
        cursor = self.text_edit.textCursor()
        block_fmt = QTextBlockFormat()
        block_fmt.setAlignment(alignment)
        cursor.mergeBlockFormat(block_fmt)
        self.text_edit.setTextCursor(cursor)

    def insert_date_plain(self):
        """Вставка дати без центрування (з поточним вирівнюванням)"""
        cursor = self.text_edit.textCursor()
        current_fmt = cursor.charFormat()
        
        # Вставка дати з поточним форматуванням
        cursor.insertText(QDate.currentDate().toString("dd.MM.yyyy"), current_fmt)
        self.text_edit.setTextCursor(cursor)

    def insert_date_centered(self):
        """Окрема функція для вставки дати по центру (якщо потрібно)"""
        cursor = self.text_edit.textCursor()
        current_fmt = cursor.charFormat()
        
        # Вставка нового абзацу з центруванням
        block_fmt = QTextBlockFormat()
        block_fmt.setAlignment(Qt.AlignCenter)
        cursor.insertBlock(block_fmt)
        
        # Вставка дати
        cursor.insertText(QDate.currentDate().toString("dd.MM.yyyy"), current_fmt)
        
        # Повернення до звичайного формату
        cursor.insertBlock()
        self.text_edit.setTextCursor(cursor)

    def toggle_bold(self):
        """Перемикач жирного тексту з комбінуванням стилів"""
        cursor = self.text_edit.textCursor()
        fmt = QTextCharFormat()
        
        # Копіюємо поточний формат
        current_fmt = cursor.charFormat()
        fmt = QTextCharFormat(current_fmt)  # Копіюємо всі налаштування
        
        # Змінюємо тільки жирність, зберігаючи інші параметри
        fmt.setFontWeight(QFont.Normal if fmt.fontWeight() > QFont.Normal else QFont.Bold)
        cursor.mergeCharFormat(fmt)
        self.text_edit.setCurrentCharFormat(fmt)

    def toggle_italic(self):
        """Перемикач курсиву з комбінуванням стилів"""
        cursor = self.text_edit.textCursor()
        current_fmt = cursor.charFormat()
        fmt = QTextCharFormat(current_fmt)  # Копіюємо поточний формат
        
        # Змінюємо тільки курсив, зберігаючи інші параметри
        fmt.setFontItalic(not current_fmt.fontItalic())
        cursor.mergeCharFormat(fmt)
        self.text_edit.setCurrentCharFormat(fmt)

    def change_color(self):
        """Зміна кольору тексту з комбінуванням стилів"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.current_color = color
            cursor = self.text_edit.textCursor()
            current_fmt = cursor.charFormat()
            fmt = QTextCharFormat(current_fmt)  # Копіюємо поточний формат
            
            # Змінюємо тільки колір, зберігаючи інші параметри
            fmt.setForeground(color)
            cursor.mergeCharFormat(fmt)
            self.text_edit.setCurrentCharFormat(fmt)

    def insert_date(self):
        """Вставка сьогоднішньої дати по центру"""
        cursor = self.text_edit.textCursor()
        
        # Зберігаємо поточний формат
        current_fmt = cursor.charFormat()
        
        # Вставка дати з центруванням
        block_fmt = QTextBlockFormat()
        block_fmt.setAlignment(Qt.AlignCenter)
        cursor.insertBlock(block_fmt)
        cursor.insertText(QDate.currentDate().toString("dd.MM.yyyy"))
        
        # Вставка нового абзацу зі звичайним форматуванням
        cursor.insertBlock()
        
        # Відновлюємо початковий формат
        cursor.setCharFormat(current_fmt)
        self.text_edit.setTextCursor(cursor)

    def on_text_changed(self):
        """Обробник зміни тексту"""
        self.save_content()

    def load_content(self):
        """Завантаження вмісту з файлу"""
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                    self.text_edit.setHtml(html_content)
        except Exception as e:
            QMessageBox.warning(None, "Помилка", f"Не вдалося завантажити нотатки: {str(e)}")

    def save_file_dialog(self):
        """Діалогове вікно збереження файлу"""
        path, _ = QFileDialog.getSaveFileName(
            self.text_edit,
            "Зберегти файл",
            "",
            "HTML файли (*.html);;Текстові файли (*.txt)"
        )
        
        if path:
            self.file_path = path
            self.save_content()
            QMessageBox.information(self.text_edit, "Успіх", "Файл успішно збережено!")

    def save_content(self):
        """Автоматичне збереження (викликається таймером)"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(self.text_edit.toHtml())
        except Exception as e:
            print(f"Помилка автозбереження: {str(e)}")

    def force_save(self):
        """Примусове збереження (кнопка)"""
        self.save_content()
        QMessageBox.information(None, "Успіх", "Нотатки збережено!")

    def get_menu_actions(self):
        """Додаємо кнопку ручного збереження"""
        from PyQt5.QtWidgets import QAction
        save_action = QAction("Зберегти", self)
        save_action.triggered.connect(self.save_content)
        return [save_action]