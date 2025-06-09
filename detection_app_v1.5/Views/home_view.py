from PyQt6.QtWidgets import (QWidget, QTabWidget, QVBoxLayout, QPushButton,
    QHBoxLayout, QListWidget, QStyle, QFrame, QProgressBar, QLabel, QScrollArea, QGridLayout)
from PyQt6.QtCore import Qt

class HomeView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        """область с выбором файлов"""
        self.file_frame = QFrame()
        self.file_frame_layout = QVBoxLayout()
        self.file_frame.setLayout(self.file_frame_layout)

        #список файлов
        self.file_frame_listFiles = QListWidget()

        #нижние кнопки
        file_frame_low_buttons_layout = QHBoxLayout()
        self.addFileButton = QPushButton("Открыть файл")
        self.addFileButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))

        self.upload_button = QPushButton("Отправить на анализ")
        self.upload_button.setEnabled(False)
        #self.cancel_upload_button = QPushButton("Отменить отправку")
        #self.cancel_upload_button.setEnabled(False)
        
        file_frame_low_buttons_layout.addWidget(self.addFileButton)
        file_frame_low_buttons_layout.addWidget(self.upload_button)
        #file_frame_low_buttons_layout.addWidget(self.cancel_upload_button)

        #Собираем область выбора файлов
        self.file_frame_layout.addWidget(self.file_frame_listFiles)
        self.file_frame_layout.addLayout(file_frame_low_buttons_layout)

        """область окон (Лево)"""
        self.tab_frame_layout = QVBoxLayout()
        #виджет окон
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        
        #построение макета области окон
        self.tab_frame_layout.addWidget(self.tabs)

        self.tab_frame = QFrame()
        self.tab_frame.setLayout(self.tab_frame_layout)

        """Область анализа файла"""
        self.analize_layout = QVBoxLayout()

        self.upload_progress_bar = QProgressBar()
        self.upload_progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.status_label = QLabel("")

        #построение области анализа файлов
        self.analize_layout.addWidget(self.upload_progress_bar)
        self.analize_layout.addWidget(self.status_label)
        
        self.tab_analize_frame = QFrame()
        self.tab_analize_frame.setLayout(self.analize_layout)

        """Область отображения ответа с сервера"""
        self.server_response_frame = QFrame()
        self.server_response_frame_layout = QVBoxLayout(self.server_response_frame)


        self.save_report_button = QPushButton("Сформировать отчет")
        self.save_report_button.setEnabled(False)

        """Объединяем область окна, область анализа и область плиток (Право)"""
        self.worker_file_frame_layout = QVBoxLayout()
        self.worker_file_frame_layout.addWidget(self.tab_frame)
        self.worker_file_frame_layout.addWidget(self.tab_analize_frame)
        self.worker_file_frame_layout.addWidget(self.server_response_frame)
        self.worker_file_frame_layout.addWidget(self.save_report_button)

        self.worker_file_frame = QFrame()
        self.worker_file_frame.setLayout(self.worker_file_frame_layout)
        
        """Построение всего макета"""
        self.main_layout = QHBoxLayout()
        
        self.main_layout.addWidget(self.file_frame)
        self.main_layout.addWidget(self.worker_file_frame)
        self.main_layout.setStretchFactor(self.worker_file_frame, 3)

        self.setLayout(self.main_layout)

