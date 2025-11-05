# core/theme_manager.py
from PyQt5.QtCore import QObject, pyqtSignal
import json, os

class ThemeManager(QObject):
    theme_changed = pyqtSignal(str)  # сигнал: "light" або "dark"

    def __init__(self):
        super().__init__()
        self.current_theme = self.load_theme()

    def load_theme(self):
        path = "theme.json"
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f).get("theme", "light")
            except:
                pass
        return "light"

    def save_theme(self):
        with open("theme.json", "w", encoding="utf-8") as f:
            json.dump({"theme": self.current_theme}, f, ensure_ascii=False, indent=2)

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.save_theme()
        self.theme_changed.emit(self.current_theme)
