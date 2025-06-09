import os
from Controllers.home_controller import HomeController
from Views.main_window import MainWindow
from Views.reports_view import ReportsView
from Utils.signal_manager import signal_manager
from PyQt6.QtCore import QObject, QPropertyAnimation, QEasingCurve, QUrl


class MainWindowController(QObject):
    
    signal_manager = signal_manager

    def __init__(self):
        super().__init__()
        self.view = MainWindow()

        # vars
        self.is_side_bar_open = True
        self.is_file_frame_open = True
        
        #MODELS\CONTROLLERS\VIEWS
        self.reports_view = ReportsView()
        self.home_controller = HomeController()

        #Страницы
        self.view.stacked_widget.addWidget(self.home_controller.view)
        self.view.stacked_widget.addWidget(self.reports_view)

        #Анимация
        self.animation = QPropertyAnimation(self.view.left_frame, b'maximumWidth')
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        #Подписка на различные сигналы внутри приложения 
        signal_manager.navigate.connect(self.handle_navigation)
        signal_manager.open_report.connect(self.display_pdf)
        
        #Слоты
        self.view.menu_button.clicked.connect(self.toggle_sidebar)
        self.view.file_frame_button.clicked.connect(self.file_frame_toggle)
    
    def toggle_sidebar(self):
        print("sidebar")
        if self.is_side_bar_open:
            self.animation.setStartValue(200)
            self.animation.setEndValue(50)
        else:
            self.animation.setStartValue(50)
            self.animation.setEndValue(200)
        self.animation.start()
        self.is_side_bar_open = not self.is_side_bar_open
    
    def handle_navigation(self, page_name):
        print(f'Навигация: {page_name}')
        if page_name == "Главная":
            self.view.stacked_widget.setCurrentWidget(self.home_controller.view)
        else:
            self.view.stacked_widget.setCurrentWidget(self.reports_view)
    
    def file_frame_toggle(self):
        print("fileframe")    
        if self.is_file_frame_open:
            self.home_controller.view.file_frame.hide()
        else:
            self.home_controller.view.file_frame.show()
        self.is_file_frame_open = not self.is_file_frame_open

    def display_pdf(self, file_path: str):
        print(f'DEBUG -> получен путь к отчету: {file_path}')

        if not os.path.exists(file_path):
            print("Ошибка: файл не найден")
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))
        pdfjs_path = os.path.join(base_dir, "resources", "pdf.js")

        html = f"""
            <html>
            <script type='text/javascript'>
                window.onload = function () {{
                    document.getElementById('viewer').src = 'file://{file_path}';
                }}
            </script>
            <body style="margin:0; padding:0;">
                <iframe id="viewer" src="" style="border: none; width: 100%; height: 100vh;" allowfullscreen></iframe>
            </body>
            </html>
        """

        self.reports_view.pdf_view.setHtml(html, QUrl.fromLocalFile(base_dir))
