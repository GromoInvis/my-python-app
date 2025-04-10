from modules.base_module import BaseModule
import importlib
import os
from PyQt5.QtWidgets import QAction
from PyQt5.QtCore import Qt

class ModuleManager:
    def __init__(self):
        self.modules = {}
        self.load_modules()
    
    def load_modules(self):
        modules_dir = "modules"
        for item in os.listdir(modules_dir):
            if os.path.isdir(os.path.join(modules_dir, item)) and item not in ["__pycache__", "base_module"]:
                try:
                    # Спеціальна обробка для Google Drive
                    if item == "google_drive":
                        self._setup_google_drive_module()
                        continue
                    
                    # Стандартна логіка для інших модулів
                    self._load_standard_module(item)
                
                except Exception as e:
                    print(f"Помилка завантаження модуля {item}: {str(e)}")
    
    def _setup_google_drive_module(self):
        """Ініціалізація модуля Google Drive з усіма перевірками"""
        try:
            # Перевірка наявності необхідних бібліотек
            import googleapiclient.discovery
            from PyQt5.QtWebEngineWidgets import QWebEngineView
            
            # Перевірка наявності credentials
            if not os.path.exists('client_secret.json'):
                print("Увага: client_secret.json не знайдено. Модуль Google Drive вимкнено.")
                return
            
            # Імпорт модуля
            from modules.google_drive.drive_ui import DriveExplorer
            
            # Створення обгортки
            class DriveWrapper(BaseModule):
                def __init__(self):
                    super().__init__("Google Drive", "icons/google_drive.png", "Хмара")
                    self.drive_ui = DriveExplorer()
                
                def create_content_widget(self):
                    return self.drive_ui
                
                def get_menu_actions(self):
                    actions = []
                    refresh_action = QAction("Оновити", self.drive_ui)
                    refresh_action.triggered.connect(self.drive_ui.load_root)
                    actions.append(refresh_action)
                    return actions
            
            self.modules["Google Drive"] = DriveWrapper()
            
        except ImportError as e:
            print(f"Google Drive вимкнено: відсутні бібліотеки ({str(e)})")
        except Exception as e:
            print(f"Помилка ініціалізації Google Drive: {str(e)}")
    
    def _load_standard_module(self, module_name):
        """Завантаження звичайних модулів"""
        try:
            module = importlib.import_module(f"modules.{module_name}")
            if hasattr(module, "register_module"):
                instance = module.register_module()
                if isinstance(instance, BaseModule):
                    self.modules[instance.name] = instance
        except Exception as e:
            print(f"Помилка завантаження {module_name}: {str(e)}")
    
    def get_module(self, name):
        return self.modules.get(name)
    
    def get_all_modules(self):
        return list(self.modules.values())