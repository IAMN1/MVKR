from pydantic import BaseModel
from typing import List

# Модель одного лемента данных
class InputDataItem(BaseModel):
    Flow_ID: str
    Source_IP: str
    Source_Port: float
    Destination_IP: str
    Destination_Port: float
    Protocol: float
    Timestamp: str
    Flow_Duration: float
    Total_Fwd_Packets: float
    Total_Backward_Packets: float
    Total_Length_of_Fwd_Packets: float
    Total_Length_of_Bwd_Packets: float
    Fwd_Packet_Length_Max: float
    Fwd_Packet_Length_Min: float
    Fwd_Packet_Length_Mean: float
    Fwd_Packet_Length_Std: float
    Bwd_Packet_Length_Max: float
    Bwd_Packet_Length_Min: float
    Bwd_Packet_Length_Mean: float
    Bwd_Packet_Length_Std: float
    Flow_Bytes_s: float
    Flow_Packets_s: float
    Flow_IAT_Mean: float
    Flow_IAT_Std: float
    Flow_IAT_Max: float
    Flow_IAT_Min: float
    Fwd_IAT_Total: float
    Fwd_IAT_Mean: float
    Fwd_IAT_Std: float
    Fwd_IAT_Max: float
    Fwd_IAT_Min: float
    Bwd_IAT_Total: float
    Bwd_IAT_Mean: float
    Bwd_IAT_Std: float
    Bwd_IAT_Max: float
    Bwd_IAT_Min: float
    Fwd_PSH_Flags: float
    Bwd_PSH_Flags: float
    Fwd_URG_Flags: float
    Bwd_URG_Flags: float
    Fwd_Header_Length: float
    Bwd_Header_Length: float
    Fwd_Packets_s: float
    Bwd_Packets_s: float
    Min_Packet_Length: float
    Max_Packet_Length: float
    Packet_Length_Mean: float
    Packet_Length_Std: float
    Packet_Length_Variance: float
    FIN_Flag_Count: float
    SYN_Flag_Count: float
    RST_Flag_Count: float
    PSH_Flag_Count: float
    ACK_Flag_Count: float
    URG_Flag_Count: float
    CWE_Flag_Count: float
    ECE_Flag_Count: float
    Down_Up_Ratio: float
    Average_Packet_Size: float
    Avg_Fwd_Segment_Size: float
    Avg_Bwd_Segment_Size: float
    Fwd_Avg_Bytes_Bulk: float
    Fwd_Avg_Packets_Bulk: float
    Fwd_Avg_Bulk_Rate: float
    Bwd_Avg_Bytes_Bulk: float
    Bwd_Avg_Packets_Bulk: float
    Bwd_Avg_Bulk_Rate: float
    Subflow_Fwd_Packets: float
    Subflow_Fwd_Bytes: float
    Subflow_Bwd_Packets: float
    Subflow_Bwd_Bytes: float
    Init_Win_bytes_forward: float
    Init_Win_bytes_backward: float
    act_data_pkt_fwd: float
    min_seg_size_forward: float
    Active_Mean: float
    Active_Std: float
    Active_Max: float
    Active_Min: float
    Idle_Mean: float
    Idle_Std: float
    Idle_Max: float
    Idle_Min: float
    Label: str

#Модель списка элементов
class InputRequest(BaseModel):
    data: List[InputDataItem]

#Модель для запросов  чанками
class ChunckRequest(BaseModel):
    session_id: str
    chunk_index: int
    is_last_chunk: bool
    data: List[InputDataItem]

#Модель для сессий
class InitSessionRequest(BaseModel):
    session_id: str
    total_chunks: int

class FinalizeSessionRequest(BaseModel):
    session_id: str
