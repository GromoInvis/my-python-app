# core/module_manager.py
from modules.base_module import BaseModule
import importlib
import os
import json
import sys
from PyQt5.QtCore import QObject, pyqtSignal
from typing import Dict, List, Optional


def get_base_path() -> str:
    """
    Повертає справжню базову директорію проєкту:
    - Для запуску з Python → директорія, де лежить main.py
    - Для .exe → директорія з exe файлом
    """
    if getattr(sys, 'frozen', False):
        # 📦 Якщо програма запущена як .exe (через PyInstaller)
        return os.path.dirname(sys.executable)

    # 🧠 Якщо запущено з вихідного коду — піднімаємося вище /core
    current = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(current, ".."))


class ModuleManager(QObject):
    modules_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.base_path = get_base_path()
        self.modules: Dict[str, BaseModule] = {}
        self.MODULE_STATE_FILE = os.path.join(self.base_path, "config", "module_state.json")

        self.enabled_modules = self._load_enabled_state()

        print(f"\n📁 Базовий шлях: {self.base_path}")
        print("⏳ Завантаження модулів...")
        self.load_modules()

    def _load_enabled_state(self) -> dict:
        if os.path.exists(self.MODULE_STATE_FILE):
            try:
                with open(self.MODULE_STATE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    print(f"🧭 Завантажено стан модулів: {data}")
                    return data
            except Exception as e:
                print(f"⚠️ Помилка читання стану: {e}")
        return {}

    def _save_enabled_state(self):
        os.makedirs(os.path.join(self.base_path, "config"), exist_ok=True)
        with open(self.MODULE_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.enabled_modules, f, indent=4, ensure_ascii=False)
        print(f"💾 Стан модулів збережено: {self.enabled_modules}")

    def set_module_enabled(self, name: str, enabled: bool):
        self.enabled_modules[name] = enabled
        self._save_enabled_state()
        self.modules_changed.emit()

    def is_module_enabled(self, name: str) -> bool:
        return self.enabled_modules.get(name, True)

    def load_modules(self):
        """Повністю перезавантажує модулі відповідно до стану."""
        modules_dir = os.path.join(self.base_path, "modules")
        self.modules.clear()

        if not os.path.exists(modules_dir):
            print(f"⚠️ Папка '{modules_dir}' не знайдена!")
            return

        for module_name in os.listdir(modules_dir):
            if self._should_skip_module(module_name):
                continue

            if not self.is_module_enabled(module_name):
                print(f"🚫 Модуль '{module_name}' вимкнено (пропускаємо).")
                continue

            try:
                module = importlib.import_module(f"modules.{module_name}")
                importlib.reload(module)
                if not hasattr(module, "register_module"):
                    continue
                instance = module.register_module()
                if not isinstance(instance, BaseModule):
                    continue

                self.modules[instance.name] = instance
                print(f"✅ {instance.name} (з '{module_name}') завантажено!")

            except Exception as e:
                print(f"⚠️ Помилка завантаження '{module_name}': {e}")

    def _should_skip_module(self, module_name: str) -> bool:
        return (
            not os.path.isdir(os.path.join(self.base_path, "modules", module_name))
            or module_name in ["__pycache__", "base_module"]
            or module_name.startswith("_")
        )

    def get_module(self, name: str) -> Optional[BaseModule]:
        return self.modules.get(name)

    def get_all_modules(self) -> List[BaseModule]:
        return list(self.modules.values())
