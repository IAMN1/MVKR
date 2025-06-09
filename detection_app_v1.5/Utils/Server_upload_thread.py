from PyQt6.QtCore import QThread, pyqtSignal
import pandas as pd
import numpy as np
import requests
import uuid

from Utils.signal_manager import signal_manager

class ServerUploadWorker(QThread):
    """
    Клиент для посылки CSV-файла на сервер порциями (чанками).
    Поддерживает инициализацию сессии, отправку чанков, завершение сессии.
    """

    signal_manager = signal_manager

    def __init__(self, file_path, chunk_size=1000, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.parent = parent

        # URL эндпоинтов
        self.url_init = 'http://127.0.0.1:5000/init_session'
        self.url_data = 'http://127.0.0.1:5000/scan_attack_from_file'
        self.url_finalize = 'http://127.0.0.1:5000/finalize_session'

        # Сессия
        self.session_id = str(uuid.uuid4())
        self.total_original_chunks = 0
        self.processed_chunks = 0

        # Статусы
        self._is_canceled = False
        self.server_response = {}

    def run(self):
        try:
            # Определяем количество строк в файле
            total_rows = self.count_rows()
            self.total_original_chunks = (total_rows + self.chunk_size - 1) // self.chunk_size
            self.signal_manager.status.emit(f'Всего строк: {total_rows}, пакетов: {self.total_original_chunks}')
            print(f'[INFO] Всего строк: {total_rows}, пакетов: {self.total_original_chunks}')

            # Инициализация сессии
            if not self.init_session():
                return

            sent_index = 0
            # Чтение и отправка чанков
            for i, chunk in enumerate(
                    pd.read_csv(self.file_path,
                                chunksize=self.chunk_size,
                                low_memory=False,
                                encoding='cp1251',
                                on_bad_lines='skip'
                            )
                        ):

                if self._is_canceled:
                    self.signal_manager.status.emit('Процесс загрузки отменен')
                    return

                clean_chunk = self.preprocess(chunk)
                if clean_chunk.empty:
                    self.signal_manager.status.emit(f'Чанк {i + 1} пуст после предобработки — пропущен')
                    continue

                is_last = sent_index == (self.total_original_chunks - 1)
                json_data = {
                    "session_id": self.session_id,
                    "chunk_index": sent_index,
                    "is_last_chunk": is_last,
                    "data": self.safe_convert_to_dict(clean_chunk)
                }

                if self.send_chunk(json_data):
                    #self.processed_chunks += 1
                    sent_index +=1
                    self.signal_manager.progress.emit(sent_index, self.total_original_chunks)

            # Завершаем сессию
            if not self._is_canceled:
                self.finalize_session()

            self.signal_manager.status.emit('Файл успешно отправлен')
            self.signal_manager.finished.emit(self.server_response)

        except Exception as ex:
            self.signal_manager.error.emit(f'Критическая ошибка: {str(ex)}')

    def count_rows(self):
        """Подсчёт строк в файле"""
        with open(self.file_path, 'r', encoding='cp1251') as f:
            return sum(1 for _ in f) - 1  # минус заголовок

    def init_session(self):
        """Инициализация сессии на сервере"""
        payload = {
            "session_id": self.session_id,
            "total_chunks": self.total_original_chunks
        }
        try:
            response = requests.post(self.url_init, json=payload, timeout=10)
            if response.status_code != 200:
                self.signal_manager.error.emit(f'Ошибка инициализации сессии: {response.status_code}')
                return False
            return True
        except Exception as ex:
            self.signal_manager.error.emit(f'Ошибка подключения к серверу при инициализации: {str(ex)}')
            return False
    
    def preprocess(self, chunk):
        """Предобработка чанка перед отправкой"""
        try:
            data = chunk.copy()

            # Очистка названий колонок
            data.columns = (
                data.columns
                .str.strip()
                .str.replace(" ", "_")
                .str.replace("/", "_")
            )

            # Удаление пустых значений и inf
            data = data.dropna()
            data.replace([np.inf, -np.inf], np.nan, inplace=True)
            data = data.dropna()

            # Конвертация object в string
            cols_obj = data.select_dtypes(include='object').columns
            data[cols_obj] = data[cols_obj].astype(str)

            # Удаление лишней колонки
            data = data.drop(columns='Fwd_Header_Length.1', errors='ignore')

            return data

        except Exception as ex:
            self.signal_manager.error.emit(f'Ошибка предобработки чанка: {str(ex)}')
            return pd.DataFrame()

    def safe_convert_to_dict(self, df):
        """Безопасная конвертация DataFrame в dict"""
        return df.astype(object).where(pd.notnull(df), None).to_dict(orient='records')

    def send_chunk(self, json_data):
        """Отправка одного чанка с повторными попытками"""
        retry_count = 3
        for attempt in range(retry_count):
            try:
                response = requests.post(
                    self.url_data,
                    json=json_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                if response.status_code == 200:
                    return True
                else:
                    self.signal_manager.error.emit(
                        f'Ошибка сервера при попытке {attempt + 1}/{retry_count}: {response.status_code}'
                    )
            except (requests.ConnectionError, requests.Timeout) as ex:
                if attempt < retry_count - 1:
                    self.signal_manager.status.emit(f'Повторная попытка ({attempt + 1}/{retry_count})')
                else:
                    self.signal_manager.error.emit(f'Не удалось отправить чанк: {str(ex)}')
                    return False
        return False

    def finalize_session(self):
        """Завершение сессии через /finalize_session"""
        #data = {"session_id": self.session_id}
        try:
            response = requests.post(
                self.url_finalize,
                data=self.session_id,  # строка в теле
                headers={'Content-Type': 'text/plain'},
                timeout=30
            )
            if response.status_code == 200:
                self.server_response = response.json()
                return True
            else:
                self.signal_manager.error.emit(f'Ошибка завершения сессии: {response.status_code}, ответ: {response.text}')
                self.server_response = {"status": "error", "error": "Finalization failed"}
                return False
        except Exception as ex:
            self.signal_manager.error.emit(f'Ошибка сети при завершении сессии: {str(ex)}')
            self.server_response = {"status": "error", "error": str(ex)}
            return False

    def cancel(self):
        self._is_canceled = True




""" class ServerUploadWorker(QThread):

    """"""ВАЖНО:
        Фозможно стоит изменить send_chun метож, чтобы в дальнейшем
          обрабатывать ответ сразу с чанков
        На данном этапе обрабатывается только финальный ответ
          после отправки на сервер финального анка
    
    """"""
    
    """"""Формат данных которые отправляет сервер:
    response = {
        "status": "success",
        "session_id": session_id,
        "predictions": response_df.to_dict(orient='records'),
        "summary": {
            "total_samples": len(response_df),
            "mallicios_count": sum(response_df['type_attack']),
            "normal_count": len(response_df['type_attack']) -  sum(response_df['type_attack'])
        }  
    }  
    """"""

    signal_manager = signal_manager

    def __init__(self, file_path, chunk_size = 1000, parent = None):
        super().__init__(parent)
        self.init_url = 'http://127.0.0.1:5000/init_session'
        self.url_data = 'http://127.0.0.1:5000/scan_attack_from_file' #scan_attack_from_file
        self.file_path = file_path
        self.chunk_size = chunk_size
        self._is_canceled = False
        self.last_chunk_sent = False
        self.session_id = str(uuid.uuid4()) # генерация уникального ID сессии
        self.processed_chunk = 0  #Счетчик реально обработанных чанков
        self.total_original_chunks = 0 # общее количество оригинальных чанков (в файле)
        self.debug_send_chunk = 0
        self.server_response = {}

    #Запуск обработки файла и отправки его на сервер
    def run(self):
        try:
            #определение общего числа строк в файле
            with open(self.file_path, 'r', encoding='cp1251') as f:
                total_rows = sum(1 for _ in f) - 1 #вычитаем заголовок
            
            #Количество оригинальных чанков (в файле)
            self.total_original_chunks = (total_rows + self.chunk_size - 1) // self.chunk_size
            self.signal_manager.status.emit(f'Всего строк в файле: {total_rows}, количество пакетов: {self.total_original_chunks}')
            print((f'Всего строк в файле: {total_rows}, количество пакетов: {self.total_original_chunks}'))
            
            
            """"""Отпарвка данных на сервер""""""
            
            #Инициализация сессии
            self.init_session(self.init_url)

            #обработка чанков
            for i, chunk in enumerate(pd.read_csv(
                self.file_path,
                chunksize=self.chunk_size,
                low_memory=False,
                encoding='cp1251'
                )):
                
                #Проверка на условие отмены
                if self._is_canceled:
                    self.signal_manager.status.emit('процесс загрузки отменен')
                    return
                
                try:
                    #Производим предподготовку данных
                    clean_data_chunk = self.preprocessing_data(chunk)

                     #проверка на последний chunk
                    if clean_data_chunk.empty:
                        self.signal_manager.status.emit(f'чанк {i+1} пуст после предобраотки, пропускается')
                        continue
                    
                    #Подготовка данных для отправки
                    json_data = {
                        "session_id" : self.session_id,
                        "chunk_index" : i,
                        "is_last_chunk" : i == (self.total_original_chunks - 1),
                        "data" : clean_data_chunk.to_dict(orient='records')
                    }
                    if self.send_chunk(self.url_data, json_data):
                        #проверяем на последний
                        self.signal_manager.progress.emit(self.processed_chunk, self.total_original_chunks)
                
                except Exception as ex:
                    self.signal_manager.error.emit(f'Ошибка при обработки чанка {i+1}: {str(ex)}')
                    continue
                finally:
                    self.processed_chunk +=1
                    self.signal_manager.progress.emit(self.processed_chunk, self.total_original_chunks)
            
            #Если не было вызвано отмены загрузки 
            # или же не было достигнуто последнего чанка
            # отправляем последний чанк 
            if  self._is_canceled == False and self.last_chunk_sent == False:
                success = self.send_final_chunk(self.url_data)
                if not success:
                    self.server_response = {"status": "error", "error": "Final chunk failed"}
            
            self.signal_manager.status.emit('Загрузка успешно завершена')
            self.signal_manager.finished.emit(self.server_response)
        
        except Exception as ex:
            self.signal_manager.error.emit(f'Критическая ошибка: {str(ex)}')
    
    def init_session(self, init_url):
        """"""Инициализация сессии на сервере""""""
        init_data = {
            "session_id": self.session_id,
            "total_chunks": self.total_original_chunks
        }

        try:
            requests.post(
                init_url,
                json=init_data,
                timeout=10
            )
        except Exception as ex:
            self.signal_manager.error.emit(f'ошибка инициализации сессии: {str(ex)}')

    def cancel(self):
        self._is_canceled = True
    
    #Предподготовка данных перед отправкой на сервер
    def preprocessing_data(self, chunk):

        try:
            #self.signal_manager.status.emit("Предобработка файла перд отправкой")

            data_chunk = chunk.copy()

            # Удаляем лишние пробелы перед и после столбцами
            #После чего заменяем пробелы и слэш между словами на _
            data_chunk.columns = (
                data_chunk.columns
                .str.strip()
                .str.replace(" ", "_")
                .str.replace("/", "_")
            )

            #Удаляем пустые строки
            data_chunk = data_chunk.dropna()

            # Датасет с логическими значениями о налии inf-Значения
            is_inf = data_chunk.isin([np.inf, -np.inf])

            #заменяем значения Infinity на Nan, после чего удаляем строки с Nan
            data_chunk.replace([np.inf, -np.inf], np.nan, inplace=True)
            data_chunk = data_chunk.dropna()

            # Получаем список столбцов с типом object
            cols_obj = data_chunk.select_dtypes('object').columns
                
            #Заменяем типы столбцов с object на string
            data_chunk[cols_obj] = data_chunk[cols_obj].astype('string')


            # Возможно колонки [Fwd Header Length.1] нет, и она была искусственно создана,
            # а, возможно и появляется при создании датасета, так или иначе, она нам не нужна,
            # так как она повторяет значения исходной колонки [Fwd Header Length], что может повлиять на
            # точность модели.
            data_chunk = data_chunk.drop(columns = 'Fwd_Header_Length.1', errors='ignore')
            return data_chunk
        
        except Exception as ex:
            self.signal_manager.error.emit(f"Ошибка предобработки данных: {ex}")
            return pd.DataFrame() # возвращаем пустой chunk, который в цикле по условию пропустится
       
    def send_chunk(self, url, json_data):
        """"""Реализация отправки с повторными попытками""""""
        retry_count = 3
        for attempt in range(retry_count):
            try:
                response = requests.post(
                    url,
                    json=json_data,
                    headers={'Content-type': 'application/json'},
                    timeout=30
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    self.signal_manager.error.emit(
                        f'Ошибка сервера при попытке {attempt+1}/{retry_count}: {response.status_code}'
                    )
            except (requests.ConnectionError, requests.Timeout) as ex:
                if attempt < retry_count - 1:
                    self.signal_manager.status.emit(
                        f'Попытка повторной отправки {attempt+1}/{retry_count}'
                    )
                    continue
                else:
                    self.signal_manager.error.emit(f'Не удалось отправить чанк: {str(ex)}')
                    return None
        return None

    def send_final_chunk(self, url):
        final_data = {
            "session_id": self.session_id,
            "chunk_index": self.total_original_chunks - 1,
            "is_last_chunk": True,
            "data": []
        }

        try:
            response = requests.post(
                url,
                json=final_data,
                headers={'Content-type': 'application/json'},
                timeout=30
            )
            if response.status_code == 200:
                self.server_response = response.json()
                self.last_chunk_sent = True
                return True
            else:
                self.signal_manager.error.emit(f'Ошибка пр иотправке финального чанка: {response.status_code}')
                self.server_response = {"status": "error", "error": "Final chunk failed"}
                return False
        except Exception as ex:
            self.signal_manager.error.emit(f'Ошибка сети при отправке финального чанка: {str(ex)}')
            self.server_response = {"status": "error", "error": str(ex)}
            return False """