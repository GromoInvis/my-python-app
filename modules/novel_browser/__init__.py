# modules/novel_browser/__init__.py
from modules.base_module import BaseModule
from modules.novel_browser.ui import NovelBrowserUI
from PyQt5.QtWidgets import QAction
from typing import List
# ❌ Видалено імпорти, які тут не потрібні
# from .save import save_translated_chapter
# from PyQt5.QtWidgets import QMessageBox


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
        """
        ⚡️ ОНОВЛЕНО: Передаємо сигнал про зміну теми безпосередньо у UI.
        """
        if self.ui:
            self.ui.apply_theme(theme_name)
        else:
            self.ui.setStyleSheet("""
                background-color: #ffffff;
                color: #000;
            """)

    def get_menu_actions(self) -> List[QAction]:
        return []

    # ──────────────────────────────
    # 🚀 Нові методи життєвого циклу
    # ──────────────────────────────
    
    def on_module_shown(self):
        """Викликається, коли цей модуль стає активним."""
        if self.ui:
            print("▶️ Novel Browser активовано, запускаю таймер.")
            self.ui.resume_sync()

    def on_module_hidden(self):
        """Викликається, коли цей модуль ховається."""
        if self.ui:
            print("⏸️ Novel Browser сховано, зупиняю таймер.")
            self.ui.pause_sync()
            
    def cleanup_module(self):
        """Викликається перед повним видаленням модуля."""
        if self.ui:
            self.ui.cleanup()
            self.ui = None


def register_module():
    return NovelBrowserWrapper()