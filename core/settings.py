import json
import os

class Settings:
    CONFIG_FILE = "config.json"

    def __init__(self):
        self.data = {
            "enabled_modules": []
        }
        self.load()

    def load(self):
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                print("⚠️ Помилка при читанні config.json, використовую стандартні налаштування.")

    def save(self):
        with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def is_module_enabled(self, name: str) -> bool:
        return name in self.data.get("enabled_modules", [])

    def set_module_enabled(self, name: str, enabled: bool):
        modules = set(self.data.get("enabled_modules", []))
        if enabled:
            modules.add(name)
        else:
            modules.discard(name)
        self.data["enabled_modules"] = list(modules)
        self.save()
