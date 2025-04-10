from .drive_ui import DriveExplorer

def register_module():
    try:
        return DriveExplorer()
    except Exception as e:
        print(f"Помилка ініціалізації Google Drive: {e}")
        return None