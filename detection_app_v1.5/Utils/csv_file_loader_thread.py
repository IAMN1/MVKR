import csv
from PyQt6.QtCore import QThread, pyqtSignal
from Utils.signal_manager import signal_manager

class CSVLoaderFileThread(QThread):
    #signal
    signal_manager = signal_manager

    def __init__(self, file_path, start_row, end_row, parent = None):
        super().__init__(parent)

        self.file_path = file_path
        self.start_row = start_row
        self.end_row = end_row
    
    def run(self):
        data = []
        with open(self.file_path, newline='', encoding='cp1251') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if self.start_row <=i < self.end_row:
                    data.append(row)
                elif i >= self.end_row:
                    break
        signal_manager.data_loaded.emit(data)
