from Controllers.file_tab_widget_controller import FileTabWidgetController
from Controllers.server_response_widget_controller import ServersResponseWidgetController
from Utils.Server_upload_thread import ServerUploadWorker
from Views.home_view import HomeView
from Utils.signal_manager import signal_manager
from Utils.report_generator import attack_report_generator

from PyQt6.QtCore import QObject, QSortFilterProxyModel
from PyQt6.QtWidgets import QFileDialog

class HomeController(QObject):
    
    signal_manager = signal_manager
    
    def __init__(self):
        super().__init__()
        self.view = HomeView()

        self.file_path = None
        self.file_tab_controller = None
        
        self.view.addFileButton.clicked.connect(self.add_File)
        self.view.tabs.tabCloseRequested.connect(self.close_tab_file)
        self.view.upload_button.clicked.connect(self.to_analize_file)
        #self.view.cancel_upload_button.clicked.connect(self.cancel_analize)
        self.view.save_report_button.clicked.connect(self.create_report_file)      
    
    
    def add_File(self=None):
        """Обработчик кнопки открытия файла"""

        file_path, _ = QFileDialog.getOpenFileName(self.view.addFileButton, 'Open File', '', 'Text Files (*.csv)')
        print(f'DEBUG -> add_file func: {file_path}')
        self.file_path = file_path
        
        #Работа с файлами
        if file_path:
            try:

                #Убираем путь до файла
                p = file_path.rfind('/')
                file_name = file_path[p+1:]

                #Добавляем файл в наш список файлов
                self.view.file_frame_listFiles.addItem(file_name)

                #передаем контроллеру окон имя файла
                self.file_tab_controller = FileTabWidgetController(file_path)
                tab = self.file_tab_controller.view
                index = self.view.tabs.addTab(tab, f'{file_path.split('/')[-1]}')
                self.view.tabs.setCurrentIndex(index)

                self.view.upload_button.setEnabled(True)
            except Exception as ex:
                print(f"Ошибка при открытии файла: {ex}")


    def close_tab_file(self, index):

        """Оработчик закрытия файла"""
        print(f"Debug -> close_tab_file_func: {index}")
        
        self.view.file_frame_listFiles.setCurrentRow(index)
        #удаление файла из списка
        currentrow = self.view.file_frame_listFiles.currentRow()
        if currentrow >= 0:
            currentItem = self.view.file_frame_listFiles.takeItem(currentrow)
            del currentItem
        
        #включаем/выключаем кнопки
        if self.view.file_frame_listFiles.count() > 0:
            self.view.upload_button.setEnabled(True)
            pass
        else:
            self.view.upload_button.setEnabled(False)
            pass

        #Закрытие окна
        tab = self.view.tabs.widget(index)
        if tab:
            self.file_tab_controller.cleanup() #очистка перед закрытием
        self.view.tabs.removeTab(index)

    def to_analize_file(self):
        """Обработчик кнопки анализа файла"""

        print("Debug-> to_analize_func")
        if not self.file_path:
            return
        
        #Меняем состояния элементов области анализа в представлении
        self.view.status_label.setText("Процесс загрузки инициализирован...")
        self.view.upload_button.setEnabled(False)
        #self.view.cancel_upload_button.setEnabled(True)

        #Создаем поток, чтобы не блокировать основное окно
        self.worker_upload = ServerUploadWorker(self.file_path)
        self.worker_upload.signal_manager.progress.connect(self.update_progress)
        self.worker_upload.signal_manager.finished.connect(self.handle_response)
        self.worker_upload.signal_manager.error.connect(self.handle_error)
        self.worker_upload.signal_manager.status.connect(self.view.status_label.setText)
        self.worker_upload.start()
        pass

    def update_progress(self, current, total):
        self.view.upload_progress_bar.setMaximum(total)
        self.view.upload_progress_bar.setValue(current)
    
    def handle_response(self, response):
        """ После получения данных с сервера
            создаем виджет отображающий ответ от сервера
        """

        self.view.status_label.setText(f'Загрузка успешно завершена')
        self.view.upload_progress_bar.reset()
        self.view.upload_button.setEnabled(True)
        #self.view.cancel_upload_button.setEnabled(False)

        #Виджет отображения ответа с сервера в табличном виде
        # Удаляем старый виджет, если он есть
        if hasattr(self, "server_response_widget_controller"):
            self.server_response_widget_controller.cleanup()
            self.server_response_widget_controller = None

        self.server_response_widget_controller = ServersResponseWidgetController()
        self.server_response_widget_controller.setup_data(response)

        
        self.view.server_response_frame_layout.addWidget(self.server_response_widget_controller.view)
        
        self.view.save_report_button.setEnabled(True)

        pass

    def handle_error(self, error_msg):
        self.view.status_label.setText(f'Ошибка: {error_msg}')
        self.view.upload_button.setEnabled(True)
        #self.view.cancel_upload_button.setEnabled(False)
        pass

    def cancel_analize(self):
        if self.worker_upload and self.worker_upload.isRunning():
            self.worker_upload.cancel()
            self.view.status_label.setText("Ожидание завершения операции...")
        pass

    def create_report_file(self):
        
        file_path, _ = QFileDialog.getSaveFileName(
            self.view.save_report_button, 
            "Сохранить отчет", 
            "", 
            "PDF file (*.pdf)"
        )

        if file_path:
            if not file_path.endswith(".pdf"):
                file_path += ".pdf"
            model = self.server_response_widget_controller.view.table_view.model()
            #определяем источник данных 
            # ( в моем случае модель обернута для сортивки в проксимодель)
            source_model = model.sourceModel() if isinstance(model, QSortFilterProxyModel) else model
            raw_data = source_model.datas

            #генерируем pdf сводку
            attack_report_generator(raw_data, file_path)

            #переходим на страницу отчетов 
            # и отображаем сформированный отчет
            signal_manager.navigate.emit("Страница отчетов")
            signal_manager.open_report.emit(file_path)
        pass
