
from Models.file_tab_open_model import FileTabOpenModel
from Views.Widgets.file_tab_widget import FileTabWidget
from PyQt6.QtCore import QObject


class FileTabWidgetController:
    def __init__(self, file_path):
        super().__init__()
        self.view = FileTabWidget()
        
        self.file_path = file_path
        self.model = None
        self.load_data()
        
        self.view.page_input.returnPressed.connect(self.goto_page)

    def load_data(self):
        print(f"Load data file tab func {self.file_path}")
        try:
            if self. file_path is not None:
                self.model = FileTabOpenModel(self.file_path) #инициализируем объект модели файла данных
                self.view.table_view.setModel(self.model)
                self.model.load_page(0)
                
                total_pages = self.model.total_pages()
                self.view.page_input.setPlaceholderText(f"страница (1 - {total_pages})")
        
        except Exception as ex:
            print(f"Ошибка загрузки данных в File_tab: {ex}")
    
    def goto_page(self):
        if self.model:
            try:
                page = int(self.view.page_input.text()) - 1
                if 0 <= page < self.model.total_pages():
                    self.model.load_page(page)
                else:
                    self.view.page_input.setText(str(self.model.current_page + 1))
            except ValueError:
                pass
    
    def cleanup(self):
        """Очищаем модель и освобождаем ресурсы при закрытии вкладки"""
        if self.model:
            self.model.cancel_loading()
            self.view.table_view.setModel(None)
            self.model = None