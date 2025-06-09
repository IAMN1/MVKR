from PyQt6.QtWidgets import (QWidget, QVBoxLayout,
    QLabel, QPushButton, QHBoxLayout, QLineEdit, QTableView
)

class ServerResponseWidget(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        #Сводная статистика (Верх)
        self.status_label = QLabel("status: waiting...")
        self.summary_label = QLabel("summary: N/A")
        
        #Панель фильтрации
        filter_layout = QHBoxLayout()
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("фильтр по данным")
        self.reset_button = QPushButton("Сброс")
        #self.reset_button.setFixedWidth(80)

        filter_layout.addWidget(self.filter_input)
        filter_layout.addWidget(self.reset_button)

        #Таблица данных
        self.table_view = QTableView()
        self.table_view.setMinimumHeight(200)

        #Построение всего макета
        layout.addWidget(self.status_label)
        layout.addWidget(self.summary_label)
        layout.addLayout(filter_layout)
        layout.addWidget(self.table_view)
        self.setLayout(layout)