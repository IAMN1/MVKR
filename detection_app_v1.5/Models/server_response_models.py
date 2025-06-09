from PyQt6.QtCore import QAbstractTableModel, Qt, QSortFilterProxyModel
from PyQt6.QtGui import QColor

COLOR_CACHE = {
        "Green": QColor("#b2fab4"),
        "Red": QColor("#f8c7c4"),
        "Orange": QColor("#ffd58a")
    }

ATTACK_TYPES = [
        "Normal",
        "Bot",
        "DDoS",
        "DoS GoldenEye",
        "DoS Hulk",
        "DoS Slowhttptest",
        "DoS slowloris",
        "FTP-Patator",
        "PortScan",
        "SSH-Patator",
        "Web Attack – Brute Force"
    ]

RED_CLASSES = [
        "Bot",
        "SSH-Patator",
        "Web Attack – Brute Force"
    ]

class PredictionTableModel(QAbstractTableModel):
    
    HEADERS = ["source IP", "Timestamp", "attack_type"]

    def __init__(self, data=None):
        super().__init__()
        self.datas = []
        self.headers = self.HEADERS


        for item in data or []: # [] чтобы избежать ошибки typeError
            attack_type_str = item.get("type_attack", "").strip()
            
            if attack_type_str == "": # при не корректных данных
                attack_label = "No or empty data" 
            elif attack_type_str in ATTACK_TYPES:
                attack_label = attack_type_str
            else:
                attack_label = "Unknown type(New)"


            self.datas.append([
                item.get("source_ip", ""),
                item.get("Timestamp", ""),
                attack_label
            ])

    def rowCount(self, parent = None):
        return len(self.datas)
    
    def columnCount(self, parent = None):
        return len(self.headers)
    
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        if role == Qt.ItemDataRole.DisplayRole:
            return self.datas[row][col]
        
        elif role == Qt.ItemDataRole.BackgroundRole and col == 2:
            
            #определение цвета на основе атаки
            attack_type = self.datas[row][2]
            if attack_type in RED_CLASSES:
                return COLOR_CACHE["Red"]
            elif attack_type == "Normal":
                return COLOR_CACHE["Green"]
            else:
                return COLOR_CACHE["Orange"]
            
        return None
    
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            
            return self.headers[section]
        
        return super().headerData(section, orientation, role)

class PredictionFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent = None):
        super().__init__(parent)
        
        self.setFilterKeyColumn(-1) #Фильтрация по всем колонкам