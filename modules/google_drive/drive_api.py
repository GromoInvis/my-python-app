import os
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from PyQt5.QtCore import QObject, pyqtSignal

class GoogleDriveAPI(QObject):
    progress_updated = pyqtSignal(int)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.service = None
        try:
            from .auth import authenticate
            self.service = build('drive', 'v3', credentials=authenticate())
        except Exception as e:
            self.error_occurred.emit(f"Помилка ініціалізації API: {str(e)}")
    
    def get_folders(self, parent_id='root'):
        try:
            results = self.service.files().list(
                q=f"'{parent_id}' in parents and mimeType='application/vnd.google-apps.folder'",
                fields="files(id, name, mimeType, modifiedTime)",
                pageSize=100
            ).execute()
            return results.get('files', [])
        except Exception as e:
            self.error_occurred.emit(f"Помилка отримання папок: {str(e)}")
            return []
    
    def get_files(self, folder_id='root'):
        try:
            results = self.service.files().list(
                q=f"'{folder_id}' in parents and mimeType!='application/vnd.google-apps.folder'",
                fields="files(id, name, mimeType, size, modifiedTime, webViewLink)",
                pageSize=100
            ).execute()
            return results.get('files', [])
        except Exception as e:
            self.error_occurred.emit(f"Помилка отримання файлів: {str(e)}")
            return []
    
    def download_file(self, file_id, file_name, save_path):
        """Завантажує файл на локальний диск"""
        try:
            # Створюємо повний шлях до файлу
            file_path = os.path.join(save_path, file_name)
            
            # Запит до Google Drive API
            request = self.service.files().get_media(fileId=file_id)
            
            # Завантаження з прогресом
            with open(file_path, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        self.progress_updated.emit(int(status.progress() * 100))
            
            return True
        except Exception as e:
            self.error_occurred.emit(f"Помилка завантаження: {str(e)}")
            return False