from PyQt6.QtCore import QObject, Qt

from Models.server_response_models import PredictionFilterProxyModel, PredictionTableModel
from Views.Widgets.server_response_widget import ServerResponseWidget

class ServersResponseWidgetController(QObject):
    def __init__(self):
        super().__init__()
        self.model = None
        self.proxy_model = None
        #Views
        self.view = ServerResponseWidget()

        #Сигналы
        self.view.filter_input.textChanged.connect(self.apply_filter)
        self.view.reset_button.clicked.connect(self.reset_filter)
    
    #Установка модели данных
    def setup_data(self, response):
        #работа с labels представления
        if response.get("status") != "success":
            self.view.status_label.setText(f'Status {response.get("status", "Unknown")}')
            return
        
        session_id = response.get("session_id", "N/A")
        self.view.status_label.setText(f'Status: Success | session ID: {session_id}')

        summary = response.get("summary", {})
        total = summary.get("total_samples", 0)
        malicious = summary.get("malicious_count", 0)
        normal = summary.get("normal_count", 0)

        self.view.summary_label.setText(
            f'Total Samples: {total} | Malicious: {malicious} | Normal: {normal}'
        )

        #Установка модели данных
        predictions = response.get("predictions", [])
        self.model = PredictionTableModel(predictions)

        #Прокси-модель для фильтрации данных
        self.proxy_model = PredictionFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

        self.view.table_view.setModel(self.proxy_model)

        #настройка таблицы
        self.view.table_view.resizeColumnsToContents()
        self.view.table_view.setSortingEnabled(True)
    
    def apply_filter(self, text):
        if self.proxy_model:
            self.proxy_model.setFilterRegularExpression(text)
    
    def reset_filter(self):
        if self.proxy_model:
            self.proxy_model.setFilterRegularExpression("")
        self.view.filter_input.clear()

    # Очистка данных
    def cleanup(self):
        print("debug-> cleanup")
        if self.proxy_model:
            self.proxy_model.deleteLater()
        if self.model:
            self.model.deleteLater()
        if self.view:
            self.view.deleteLater()
        
       