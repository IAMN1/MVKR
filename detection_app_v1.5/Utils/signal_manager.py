from PyQt6.QtCore import QObject, pyqtSignal

class SignalManager(QObject):
    #сигнал для навигации между страницами
    navigate = pyqtSignal(str)

    #сигнал для передачи пути файла отчета
    open_report = pyqtSignal(str)

    #сохранение состояния данных
    save_data = pyqtSignal(str,str) #key, value
    data_loaded = pyqtSignal(list)

    #Server_upload_thread
    progress = pyqtSignal(int, int) # текущий шаг, общий шаг
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    status = pyqtSignal(str)

#Глобальный сигнал
signal_manager = SignalManager()