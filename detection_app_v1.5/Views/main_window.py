from PyQt6.QtWidgets import (QMainWindow, QHBoxLayout, QWidget, QFrame,
    QVBoxLayout,QPushButton, QStackedWidget, QStyle)
from PyQt6.QtCore import Qt
from Utils.signal_manager import signal_manager


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Каркас")
        self.resize(1400,900)
        #self.setStyleSheet(load_stylesheet())

        #центральный виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        #Основной layout
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)

        """Боковое меню (Лево)"""
        self.side_bar_menu = QFrame()
        self.side_bar_menu.setObjectName('sidebar')
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        #пункты меню
        for item in ["Главная", "Отчеты"]:
            btn = QPushButton(text=item)
            btn.setObjectName(f'btn_{item.lower()}')
            btn.clicked.connect(lambda  checked, name=item: signal_manager.navigate.emit(name))
            layout.addWidget(btn)
        self.side_bar_menu.setLayout(layout)

        self.menu_button = QPushButton("☰")
        self.menu_button.setFixedSize(40,40)

        #Левый контейнер (меню) + кнопка
        self.left_container = QVBoxLayout()
        self.left_container.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.left_container.addWidget(self.menu_button)
        self.left_container.addWidget(self.side_bar_menu)

        self.left_frame = QFrame()
        self.left_frame.setLayout(self.left_container)

        
        """область основного пространства"""
        self.content_area = QFrame()
        self.content_area.setObjectName("contentArea")

        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0,0,0,0)
        self.content_layout.setSpacing(0)
        
        #Добавляем страницы
        self.stacked_widget = QStackedWidget()
        self.content_layout.addWidget(self.stacked_widget)

        """Боковое меню (Право)"""
        self.right_side_bar_menu = QFrame()
        self.right_sb_layout = QHBoxLayout(self.right_side_bar_menu)
        self.right_sb_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.file_frame_button = QPushButton()
        self.file_frame_button.setIcon(self.style().standardIcon(
                                QStyle.StandardPixmap.SP_FileLinkIcon))
        self.right_sb_layout.addWidget(self.file_frame_button)


        #Добавляем все на экран
        self.main_layout.addWidget(self.left_frame)
        self.main_layout.addWidget(self.content_area)
        self.main_layout.addWidget(self.right_side_bar_menu)

    
