import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from core.app import MyApp

# Важливо: ці налаштування мають бути перед створенням QApplication
if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)  # Необхідно для QtWebEngine
    app = QApplication(sys.argv)
    
    # Ініціалізація головного вікна
    main_app = MyApp()
    main_app.run()