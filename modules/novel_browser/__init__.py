from modules.base_module import BaseModule
from modules.novel_browser.ui import NovelBrowserUI
from PyQt5.QtWidgets import QAction
from typing import List
from .save import save_translated_chapter
from PyQt5.QtWidgets import QMessageBox


class NovelBrowserWrapper(BaseModule):
    def __init__(self):
        super().__init__(
            name="Novel Browser",
            icon="icons/book.png",
            category="Читання"
        )
        self.ui = NovelBrowserUI()

    def create_content_widget(self):
        return self.ui
    
    def on_theme_changed(self, theme_name: str):
        if theme_name == "dark":
            self.ui.setStyleSheet("""
                background-color: #121212;
                color: #ddd;
            """)
        else:
            self.ui.setStyleSheet("""
                background-color: #ffffff;
                color: #000;
            """)

    def get_menu_actions(self) -> List[QAction]:
        return []


def register_module():
    return NovelBrowserWrapper()
