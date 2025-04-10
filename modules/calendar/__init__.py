from .calendar import CalendarModule

def register_module():
    """Фабрична функція для реєстрації модуля"""
    return CalendarModule()  # Просто створює екземпляр без використання self