from PyQt6.QtWidgets import QVBoxLayout, QWidget, QTableView, QLineEdit

#from Controllers.file_tab_widget_controller import FileTabWidgetController

class FileTabWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()

        self.page_input = QLineEdit()
        self.page_input.setMaximumWidth(300)
        self.page_input.setMinimumWidth(300)
        
        self.table_view = QTableView()
        
        self.layout.addWidget(self.page_input)
        self.layout.addWidget(self.table_view)

        self.setLayout(self.layout)