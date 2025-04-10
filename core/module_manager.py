from modules.base_module import BaseModule
import importlib
import os
from PyQt5.QtWidgets import QAction
from PyQt5.QtCore import Qt
from typing import Dict, List, Optional, Type

class ModuleManager:
    def __init__(self):
        self.modules: Dict[str, BaseModule] = {}
        print("\n⏳ Завантаження модулів...")
        self.load_modules()
    
    def load_modules(self) -> None:
        """Завантажує всі доступні модулі з папки 'modules'"""
        modules_dir = "modules"
        for module_name in os.listdir(modules_dir):
            if self._should_skip_module(module_name):
                continue
            
            print(f"\n🔍 Модуль: {module_name}")
            try:
                if module_name == "google_drive":
                    self._load_google_drive()
                else:
                    self._load_standard_module(module_name)
            except Exception as e:
                print(f"❌ Помилка: {str(e)}")
    
    def _should_skip_module(self, module_name: str) -> bool:
        """Перевіряє, чи потрібно ігнорувати модуль"""
        return (
            not os.path.isdir(f"modules/{module_name}") 
            or module_name in ["__pycache__", "base_module"]
            or module_name.startswith("_")
        )
    
    def _load_google_drive(self) -> None:
        """Спеціальна ініціалізація для Google Drive"""
        try:
            # Перевірка залежностей
            self._check_google_dependencies()
            
            # Імпорт через try-except для зручності
            from modules.google_drive.drive_ui import DriveExplorer
            
            class DriveModuleWrapper(BaseModule):
                def __init__(self):
                    super().__init__(
                        name="Google Drive",
                        icon="icons/google_drive.png",
                        category="Хмара"
                    )
                    self._ui = DriveExplorer()
                
                def create_content_widget(self):
                    return self._ui
                
                def get_menu_actions(self) -> List[QAction]:
                    actions = []
                    refresh_action = QAction("Оновити", self._ui)
                    refresh_action.triggered.connect(self._ui.load_root)
                    actions.append(refresh_action)
                    return actions
            
            self.modules["Google Drive"] = DriveModuleWrapper()
            print("✅ Google Drive успішно підключено!")
            
        except Exception as e:
            print(f"❌ Google Drive недоступний: {str(e)}")
    
    def _check_google_dependencies(self) -> None:
        """Перевіряє наявність бібліотек та файлів для Google Drive"""
        required_libs = [
            ("googleapiclient.discovery", "google-api-python-client"),
            ("PyQt5.QtWebEngineWidgets", "PyQtWebEngine")
        ]
        
        for lib, pip_name in required_libs:
            try:
                importlib.import_module(lib)
            except ImportError:
                raise ImportError(f"Встановіть '{pip_name}': pip install {pip_name}")
        
        if not os.path.exists('client_secret.json'):
            raise FileNotFoundError("Відсутній client_secret.json (див. інструкції)")
    
    def _load_standard_module(self, module_name: str) -> None:
        """Завантажує звичайний модуль"""
        try:
            module = importlib.import_module(f"modules.{module_name}")
            
            if not hasattr(module, "register_module"):
                raise AttributeError("Немає register_module()")
                
            instance = module.register_module()
            
            if not isinstance(instance, BaseModule):
                raise TypeError("Модуль має успадковувати BaseModule")
                
            self.modules[instance.name] = instance
            print(f"✅ {instance.name} завантажено!")
            
        except Exception as e:
            print(f"⚠️ Помилка: {type(e).__name__} - {str(e)}")
    
    def get_module(self, name: str) -> Optional[BaseModule]:
        return self.modules.get(name)
    
    def get_all_modules(self) -> List[BaseModule]:
        return list(self.modules.values())