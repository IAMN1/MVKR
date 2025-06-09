from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWebEngineWidgets import QWebEngineView
from Utils.helpers import emit_signal

class ReportsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        #Виджет отчетов
        self.pdf_view = QWebEngineView()
        self.pdf_view.settings().setAttribute(
            self.pdf_view.settings().WebAttribute.PluginsEnabled,
            True
        )
        self.pdf_view.settings().setAttribute(
            self.pdf_view.settings().WebAttribute.PdfViewerEnabled,
            True
        )

        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.close)

        layout.addWidget(self.pdf_view)
        layout.addWidget(close_button)
    