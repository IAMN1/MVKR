from typing import List
import pandas as pd
import pickle

#Старая модель
#with open('Server\webattack_detection_model.pkl', 'rb') as f:
#    model = pickle.load(f)

with open('Server\\rf_final_model.pkl', 'rb') as f:
    model = pickle.load(f)   

def preprocessing_data(data) -> pd.DataFrame:
    """
        функция препроцессинга данных, 
        перед подачей в модель
    """
    try:

        #оставляем признаки, подогнаные под модель
        features_for_model = [
                'Flow_Duration', 'Total_Fwd_Packets','Total_Length_of_Fwd_Packets',
                'Fwd_Packet_Length_Max','Fwd_Packet_Length_Mean','Bwd_Packet_Length_Max',
                'Bwd_Packet_Length_Min','Flow_Bytes_s','Flow_Packets_s','Flow_IAT_Mean',
                'Flow_IAT_Min','Fwd_IAT_Min','Bwd_IAT_Total','Bwd_IAT_Mean',
                'Fwd_Header_Length','Bwd_Packets_s','PSH_Flag_Count'
        ]

        preprocessed_df = data[features_for_model]
        
        return preprocessed_df

    except Exception as ex:
        raise ValueError(f"Ошибка при подготовки DataFrame: {str(ex)}")

def scan_file_to_attack(pydantic_data: List) -> dict[str, any]:

    """
       Основная функция -  Функция предсказания
    """

    #одготовка данных для модели
    df = pd.DataFrame([item.model_dump() for item in pydantic_data])
    df_for_model = preprocessing_data(df)

    #Предсказание
    predict = (model.predict(df_for_model.values)).tolist()

    #Преобразование числовых значений в категориальные данные
    encode_predict = prediction_decode(predict)

    #формирует датафрейм для ответа
    data_for_response_df = [{"source_ip": item.Source_IP, "Timestamp": item.Timestamp} for item in pydantic_data]
    response_df = pd.DataFrame(data_for_response_df)

    response_df['type_attack'] = encode_predict

    return create_response(response_df)

def prediction_decode(pred_encode):
    """
        Функция декодирования предсказания модели
        из числавого в тектовый
    """

    label_mapping = {
        0: "Normal",
        1: "Bot",
        2: "DDoS",
        3: "DoS GoldenEye",
        4: "DoS Hulk",
        5: "DoS Slowhttptest",
        6: "DoS slowloris",
        7: "FTP-Patator",
        8: "PortScan",
        9: "SSH-Patator",
        10: "Web Attack – Brute Force"
    }

    y_decoded_label = [label_mapping[pred] for pred in pred_encode]

    return y_decoded_label

def create_response(response_df):
    """
       Функция, формирующая часть ответа для отправки клиенту
    """
    
    total_samples = len(response_df)
    malicious_count = response_df[response_df['type_attack'] != 'Normal'].shape[0]
    normal_count = response_df[response_df['type_attack'] == 'Normal'].shape[0]

    response = {
        "predictions": response_df.to_dict(orient='records'),
        "summary": {
            "total_samples": total_samples,
            "malicious_count": malicious_count,
            "normal_count": normal_count
        }  
    }  
    return response
