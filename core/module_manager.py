from modules.base_module import BaseModule
import importlib
import os

class ModuleManager:
    def __init__(self):
        self.modules = {}
        self.load_modules()
    
    def load_modules(self):
        modules_dir = "modules"
        for item in os.listdir(modules_dir):
            if os.path.isdir(os.path.join(modules_dir, item)) and item != "__pycache__":
                try:
                    module = importlib.import_module(f"modules.{item}")
                    if hasattr(module, "register_module"):
                        module_instance = module.register_module()
                        if isinstance(module_instance, BaseModule):
                            self.modules[module_instance.name] = module_instance
                except ImportError as e:
                    print(f"Error loading module {item}: {e}")
    
    def get_module(self, name):
        return self.modules.get(name)
    
    def get_all_modules(self):
        return list(self.modules.values())