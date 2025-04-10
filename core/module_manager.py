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
        print(f"⏳ Початок завантаження модулів з папки '{modules_dir}'...")
        
        for item in os.listdir(modules_dir):
            module_path = os.path.join(modules_dir, item)
            
            # Ігноруємо непапки та службові папки
            if not os.path.isdir(module_path) or item in ["__pycache__", "base_module"]:
                continue
                
            # Перевіряємо наявність __init__.py
            if not os.path.exists(os.path.join(module_path, "__init__.py")):
                print(f"⚠️ Увага: Папка '{item}' не містить __init__.py - ігнорується")
                continue
                
            print(f"🔍 Обробка модуля: {item}")
            try:
                self._load_standard_module(item)
            except Exception as e:
                print(f"❌ Помилка завантаження модуля {item}: {str(e)}")
    
    def _load_standard_module(self, module_name):
        """Завантаження стандартного модуля"""
        try:
            module = importlib.import_module(f"modules.{module_name}")
            
            if not hasattr(module, "register_module"):
                print(f"⚠️ Модуль {module_name} не має функції register_module()")
                return
                
            instance = module.register_module()
            
            if not isinstance(instance, BaseModule):
                print(f"⚠️ Модуль {module_name} не успадковує BaseModule")
                return
                
            self.modules[instance.name] = instance
            print(f"✅ Модуль '{instance.name}' успішно завантажено!")
            
        except ImportError as e:
            print(f"❌ Помилка імпорту модуля {module_name}: {str(e)}")
        except Exception as e:
            print(f"❌ Критична помилка в модулі {module_name}: {str(e)}")
    
    def get_module(self, name):
        return self.modules.get(name)
    
    def get_all_modules(self):
        return list(self.modules.values())