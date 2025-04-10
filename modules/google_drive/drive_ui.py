import os
import platform
import subprocess
from urllib.parse import unquote
from googleapiclient.http import MediaIoBaseDownload
from PyQt5.QtWidgets import (QWidget, QTreeView, QListView, QSplitter, QVBoxLayout, 
                            QFileDialog, QProgressDialog, QMessageBox, QMenu, 
                            QInputDialog, QLabel)
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtCore import Qt, QPoint, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from .drive_api import GoogleDriveAPI


WEBENGINE_AVAILABLE = False
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    WEBENGINE_AVAILABLE = True
except ImportError:
    print("Увага: QtWebEngine не встановлено. Попередній перегляд буде обмежено")


class DriveExplorer(QWidget):
    def __init__(self):
        super().__init__()
        self.preview_window = None  # Посилання на вікно перегляду
        self.api = GoogleDriveAPI()
        self.current_folder = 'root'
        self.selected_file = None
        self.init_ui()
        self.load_root()
        
        # Підключення сигналів
        self.api.progress_updated.connect(self.update_progress)
        self.api.error_occurred.connect(self.show_error)

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        
        # Панель статусу
        self.status_label = QLabel("Підключення до Google Drive...")
        self.layout.addWidget(self.status_label)
        
        # Поділ на дві панелі
        self.splitter = QSplitter()
        
        # Дерево папок
        self.tree_view = QTreeView()
        self.tree_model = QStandardItemModel()
        self.tree_view.setModel(self.tree_model)
        self.tree_view.setHeaderHidden(True)
        self.tree_view.clicked.connect(self.on_folder_clicked)
        
        # Список файлів
        self.list_view = QListView()
        self.list_model = QStandardItemModel()
        self.list_view.setModel(self.list_model)
        self.list_view.doubleClicked.connect(self.on_file_double_clicked)
        self.list_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_view.customContextMenuRequested.connect(self.show_context_menu)
        
        self.splitter.addWidget(self.tree_view)
        self.splitter.addWidget(self.list_view)
        self.layout.addWidget(self.splitter)
        
        # Діалог прогресу
        self.progress = QProgressDialog("Завантаження...", "Скасувати", 0, 100, self)
        self.progress.setWindowTitle("Завантаження файлу")
        self.progress.setWindowModality(Qt.WindowModal)
        self.progress.close()

    def load_root(self):
        self.status_label.setText("Завантаження структури папок...")
        self.tree_model.clear()
        
        # Додаємо кореневу папку
        root_item = QStandardItem(QIcon("icons/drive.png"), "Google Drive")
        root_item.setData('root', Qt.UserRole)
        self.tree_model.appendRow(root_item)
        
        # Завантажуємо вміст кореневої папки
        self.load_folder_content('root')
        self.status_label.setText("Готово")

    def on_folder_clicked(self, index):
        folder_id = index.data(Qt.UserRole)
        self.current_folder = folder_id
        self.load_folder_content(folder_id)

    def load_folder_content(self, folder_id):
        self.list_model.clear()
        files = self.api.get_files(folder_id)
        
        for file in files:
            item = QStandardItem(self.get_file_icon(file['mimeType']), file['name'])
            item.setData(file, Qt.UserRole)
            self.list_model.appendRow(item)

    def get_file_icon(self, mime_type):
        # Підставте свої іконки для різних типів файлів
        if 'folder' in mime_type:
            return QIcon("icons/folder.png")
        elif 'image' in mime_type:
            return QIcon("icons/image.png")
        elif 'pdf' in mime_type:
            return QIcon("icons/pdf.png")
        else:
            return QIcon("icons/file.png")

    def show_context_menu(self, pos):
        index = self.list_view.indexAt(pos)
        if not index.isValid():
            return
            
        self.selected_file = index.data(Qt.UserRole)
        menu = QMenu()
        
        # Дії для контекстного меню
        open_action = menu.addAction(QIcon("icons/open.png"), "Відкрити")
        download_action = menu.addAction(QIcon("icons/download.png"), "Завантажити")
        
        # Обробник для кнопки "Завантажити"
        download_action.triggered.connect(self._handle_download)
        
        # Обробник для кнопки "Відкрити"
        open_action.triggered.connect(self.preview_file)
        
        menu.exec_(self.list_view.mapToGlobal(pos))

    def _handle_download(self):
        """Обробник завантаження файлу"""
        if not self.selected_file:
            return
            
        # Запит папки для збереження
        save_path = QFileDialog.getExistingDirectory(
            self, 
            "Виберіть папку для збереження",
            os.path.expanduser("~")
        )
        
        if save_path:
            self.progress.show()
            try:
                # Викликаємо API для завантаження
                result = self.api.download_file(
                    file_id=self.selected_file['id'],
                    file_name=self.selected_file['name'],
                    save_path=save_path
                )
                
                if result:
                    QMessageBox.information(
                        self, 
                        "Успіх", 
                        f"Файл {self.selected_file['name']} успішно завантажено!"
                    )
            except Exception as e:
                QMessageBox.warning(
                    self, 
                    "Помилка", 
                    f"Не вдалося завантажити файл: {str(e)}"
                )
            finally:
                self.progress.close()

    def download_file(self, file_id, file_name, save_path):
        """Завантажує файл і повертає шлях до завантаженого файлу"""
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_path = os.path.join(save_path, file_name)
            
            with open(file_path, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        self.progress_updated.emit(int(status.progress() * 100))
            return file_path  # Повертаємо шлях до файлу
        except Exception as e:
            self.error_occurred.emit(f"Помилка завантаження: {str(e)}")
            return None

    def preview_file(self):
        if not self.selected_file:
            return

        # Отримуємо тимчасову папку
        temp_dir = os.path.join(os.path.expanduser("~"), "temp_google_drive")
        os.makedirs(temp_dir, exist_ok=True)

        # Завантажуємо файл тимчасово
        temp_path = os.path.join(temp_dir, unquote(self.selected_file['name']))
        
        self.progress.show()
        try:
            if self.api.download_file(self.selected_file['id'], 
                                    self.selected_file['name'], 
                                    temp_dir):
                self._open_file_with_default_app(temp_path)
        finally:
            self.progress.close()

    def _open_file_with_default_app(self, file_path):
        """Відкриває файл у програмі за замовчуванням"""
        try:
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # MacOS
                subprocess.run(['open', file_path], check=True)
            else:  # Linux та інші Unix-системи
                subprocess.run(['xdg-open', file_path], check=True)
        except Exception as e:
            QMessageBox.warning(self, "Помилка", 
                              f"Не вдалося відкрити файл: {str(e)}")

    def share_file(self):
        if self.selected_file:
            email, ok = QInputDialog.getText(self, "Поділитися", "Введіть email:")
            if ok and email:
                QMessageBox.information(self, "Успіх", 
                    f"Запит на доступ до {self.selected_file['name']} відправлено на {email}")

    def update_progress(self, value):
        self.progress.setValue(value)
        if value >= 100:
            self.progress.close()

    def show_error(self, message):
        QMessageBox.critical(self, "Помилка", message)
        self.status_label.setText("Сталася помилка")

    def on_file_double_clicked(self, index):
        self.selected_file = index.data(Qt.UserRole)
        self.preview_file()