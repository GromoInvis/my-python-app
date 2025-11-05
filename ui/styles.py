# ui/styles.py

LIGHT_THEME = {
    "MAIN": """
        QMainWindow {
            background-color: #ffffff;
            color: #222;
        }
        QMenuBar, QMenu {
            background-color: #f8f9fa;
            color: #222;
        }
        QMenuBar::item:selected, QMenu::item:selected {
            background-color: #dcdcdc;
        }
    """,
    "SIDEBAR": """
        QWidget {
            background-color: #f8f9fa;
            border-right: 1px solid #dee2e6;
            color: #222;
        }
    """
}

DARK_THEME = {
    "MAIN": """
        QMainWindow {
            background-color: #121212;
            color: #ddd;
        }
        QMenuBar, QMenu {
            background-color: #1e1e1e;
            color: #ddd;
        }
        QMenuBar::item:selected, QMenu::item:selected {
            background-color: #333;
        }
    """,
    "SIDEBAR": """
        QWidget {
            background-color: #1e1e1e;
            border-right: 1px solid #2c2c2c;
            color: #ddd;
        }
    """
}
