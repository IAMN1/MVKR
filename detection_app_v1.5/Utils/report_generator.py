import os
from fpdf import FPDF
from fpdf.fonts import FontFace
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from io import BytesIO
import numpy as np
import tempfile

def attack_report_generator(data, filename='report.pdf'):
    """
        функция создания краткой сводки в PDF

        data - список записей, где каждая запись - список из 3 значений:
        [source_ip, timestamp, attack_type]
    
    """

    #Подсчет статистики
    attack_counter = {}
    for item in data:
        attack_type = item[2].strip()
        if attack_type == "":
            continue
        attack_counter[attack_type] = attack_counter.get(attack_type, 0) + 1

    total_samples = len(data)
    normal_count = attack_counter.get("Normal", 0)
    malicious_count = total_samples - normal_count
    
    labels = list(attack_counter.keys())
    values = list(attack_counter.values())

    #Создаем столбчатый график
    fig, ax = plt.subplots(figsize=(12, 5))
    colors = ["#b2fab4" if label == "Normal" 
                else "#f8c7c4" if label in ["Bot", "SSH-Patator", "Web Attack – Brute Force"] 
                else "#ffd58a" for label in labels]
    
    ax.bar(labels, values, color=colors)
    ax.set_yscale('log')
    ax.set_title("Распределение типов атак")
    ax.set_xlabel("Тип атаки")
    ax.set_ylabel("Количество")
    ax.grid(True)
    # Поворачиваем метки на оси X для лучшей читаемости
    ax.set_xticklabels(labels, rotation=45, ha='right')

    #Сохраняем график как временный файл 
    # чтобы избежать ошибки с bytesIO
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmpFile:
        img_path = tmpFile.name
        plt.savefig(img_path, format='png', bbox_inches='tight')
    plt.close()

    # img_data = BytesIO()
    # #canvas = FigureCanvas(fig)
    # #canvas.print_png(img_data, bbox_inches='tight')
    # plt.savefig(img_data, format='png', bbox_inches='tight')
    # plt.close()
    #
    ##перемотка bytesIO в начало
    #img_data.seek(0)

    # PDF
    pdf = FPDF()
    pdf.add_page()
    
    # шрифт с поддержкой кириллицы
    pdf.add_font("DejaVu", fname="Resources\\DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", size=12)

    pdf.cell(0,10, txt="Отчет по анализу сетевого трафика", ln=True, align='C')

    #сводная инфа
    pdf.ln(10)
    pdf.cell(0,10, txt=f'Общее количество записей: {total_samples}', ln=True)
    pdf.cell(0,10, txt=f'Нормальный трафик: {normal_count}', ln=True)
    pdf.cell(0,10, txt=f'Аномальный трафик: {malicious_count}', ln=True)

    pdf.ln(10)
    pdf.cell(0,10, txt="Распределение атак: ", ln=True)

    #Таблица с колличеством атак
    pdf.set_font_size(10)
    col_width = [50,40,40]
    pdf.cell(col_width[0], 10, txt="Тип атаки", border=1)
    pdf.cell(col_width[1], 10, txt="Колличество", border=1)
    pdf.cell(col_width[2], 10, txt="соотношение (%)", border=1, ln=True)

    for label, value in attack_counter.items():
        percent = (value / total_samples) * 100
        pdf.cell(col_width[0], 10, txt=label, border=1)
        pdf.cell(col_width[1], 10, txt=str(value), border=1)
        pdf.cell(col_width[2], 10, txt=f'{percent:.2f}', border=1, ln=True)
    
    pdf.ln(5)
    pdf.set_font_size(12)

    #Вставляем график
    pdf.image(img_path, x=10, w=190)

    #Созранение в файл
    pdf.output(filename)
    print(f"DEBUG -> Отчет создан: {filename}")

    try:
        #Удаление временного файла
        os.remove(img_path)
    except OSError as ex:
        print(f"ОШибка при удалении временного файла содержащего график! {ex} ")