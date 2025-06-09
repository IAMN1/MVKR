from PyQt6.QtCore import QAbstractTableModel, Qt, QVariant
import csv

from Utils.csv_file_loader_thread import CSVLoaderFileThread

class FileTabOpenModel(QAbstractTableModel):

    def __init__(self, file_path, parent = None):
        super().__init__(parent)

        self.file_path = file_path
        self.data_cache = [] # кэш текущей страницы
        self.headers = []
        self.total_rows = 0
        self.current_page = 0
        self.rows_per_page = 1000 # размер одной тсраницы
        self._load_headers()

    def _load_headers(self):
        with open(self.file_path, newline='', encoding='cp1251') as f:
            reader = csv.reader(f)
            self.headers = next(reader)
            self.total_rows = sum(1 for _ in reader) + 1 # + 1 для заголовка
    
    def load_page(self, page):
        start_row = page * self.rows_per_page
        end_row = min((page + 1) * self.rows_per_page, self.total_rows)

        self.loader_thread = CSVLoaderFileThread(self.file_path, start_row, end_row, self)
        self.loader_thread.signal_manager.data_loaded.connect(self._on_data_loaded)
        self.loader_thread.start()

        with open(self.file_path, newline='', encoding='cp1251') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if start_row <= i < end_row:
                    self.data_cache.append(row)
                elif i >= end_row:
                    break
        self.endResetModel()

    def _on_data_loaded(self, data):
        self.beginResetModel()
        self.data_cache = data
        self.endResetModel()

    def rowCount(self, parent = None):
        return len(self.data_cache)
    
    def columnCount(self, parent = None):
        return len(self.headers)
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            return self.data_cache[index.row()][index.column()]
        return QVariant()
    
    def total_pages(self):
        return (self.total_rows + self.rows_per_page - 1) // self.rows_per_page
    
    def cancel_loading(self):
        if hasattr(self, 'loader_thread') and self.loader_thread.isRunning():
            self.loader_thread.quit()
            self.loader_thread.wait()
        pass