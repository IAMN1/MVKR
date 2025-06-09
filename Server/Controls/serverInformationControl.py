import time

"""
    Контроллер отвечающий за информацию по статусу сервера
"""

def get_uptime(start_time):

    seconds = int(time.time() - start_time)
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return f"{days} дн. {hours} ч. {minutes} мин. {seconds} сек."