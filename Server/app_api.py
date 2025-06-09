from datetime import datetime
import time
import psutil
import platform
from typing import List
from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

from DataModels.DataModel import InitSessionRequest, ChunckRequest, InputDataItem, FinalizeSessionRequest
from Controls import scanAttackControl as sa_control
from Controls.serverInformationControl import get_uptime

app = FastAPI()

 #Временное хранилище сессий в памяти
CHUNK_STORAGE: dict[str, list[list[InputDataItem]]] = {}

start_time = time.time()

@app.get("/Server_Heath")
def ServerHealth():

    server_status = "healthy"
    
    uptime = get_uptime(start_time)

    system_info = {
        "os": platform.system(),
        "os_version": platform.version(),
        "uptime": uptime,
        "cpu_usage": psutil.cpu_percent(interval=0.1),
        "memory_usage": psutil.virtual_memory().percent,
        "status": server_status
    }

    html = f"""
    <html>
        <head>
            <title>Server Status</title>
            <style>
                body {{
                    background-color: #f2f2f2;
                    font-family: Arial, sans-serif;
                    text-align: center;
                    padding: 50px;
                }}
                .container {{
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                    max-width: 500px;
                    margin: auto;
                }}
                h1 {{
                    color: #2c3e50;
                }}
                .status {{
                    color: green;
                    font-weight: bold;
                }}
                .info {{
                    margin-top: 20px;
                    text-align: left;
                }}
                .info p {{
                    margin: 5px 0;
                }}
                footer {{
                    margin-top: 40px;
                    font-size: 0.9em;
                    color: #aaa;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🌐 Статус сервера</h1>
                <p>Сервер работает нормально.</p>
                <p class="status">Статус: Healthy</p>

                <div class="info">
                    <p>ОС: {system_info['os']}</p>
                    <p>Время работы: {system_info['uptime']}</p>
                    <p>CPU загруженность: {system_info['cpu_usage']}%</p>
                    <p>Память используется: {system_info['memory_usage']}%</p>
                </div>

                <footer>
                    &copy; {datetime.now().year} Мониторинг сервера
                </footer>
            </div>
        </body>
    </html>
    """
    return HTMLResponse(content=html)

#Инициализация сессий
@app.post("/init_session")
async def init_session(payload: InitSessionRequest):
    session_id = payload.session_id
    total_chunks = payload.total_chunks

    if not session_id or not isinstance(session_id, str):
        raise HTTPException(status_code=400, detail="session_id должен быть строкой")

    CHUNK_STORAGE[session_id] = {
        "total_chunks": total_chunks,
        "received_chunks": 0,
        "data": [],
        "is_complete": False
    }

    return {"status": "ok", "message": "Сессия инициализирована"}

#Для запросов чанками
@app.post("/scan_attack_from_file")
async def receive_chunk(request: ChunckRequest):
    try:

        session_id = request.session_id
        chunk_index = request.chunk_index
        is_last_chunk = request.is_last_chunk
        data = request.data

        if session_id not in CHUNK_STORAGE:
            raise HTTPException(status_code=400, detail="сессия не найдена")

        session = CHUNK_STORAGE[session_id]
        if session["is_complete"]:
            raise HTTPException(status_code=400, detail="Сессия завершена")

        # Сохранение данных
        session["data"].extend(data)
        session["received_chunks"] += 1

        # Логирование
        print(f"[SERVER] Получен чанк {chunk_index} для сессии {session_id}. Всего получено: {session['received_chunks']}/{session['total_chunks']}")

        if is_last_chunk:
            print(f"[SERVER] Последний чанк получен для сессии {session_id}")

        return {"status": "ok", "chunk_received": chunk_index}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки чанка: {str(e)}")

@app.post("/finalize_session")
async def finalize_session(request: Request):
    session_id = (await request.body()).decode("utf-8").strip()

    if not session_id or session_id not in CHUNK_STORAGE:
        raise HTTPException(status_code=400, detail="Неверный или отсутствующий session_id")

    session = CHUNK_STORAGE[session_id]

    #Проверка на завершенную сессию
    if session["is_complete"]:
        return {"status": "Сессия уже завершена", "result": session.get("result")}

    #Предикт модели
    predict = sa_control.scan_file_to_attack(session["data"])


    # Здесь можно запустить финальную обработку
    print(f"[SERVER] Завершение сессии {session_id}, всего записей: {len(session['data'])}")

    result = {
        "status": "success",
        "session_id": session_id,
    }

    #Объединение result и predict
    result.update(predict)

    # Потенциально для бд - если будет 
    session["result"] = result
    session["is_complete"] = True

    #Очистка памяти
    del CHUNK_STORAGE[session_id]

    return result

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print("Validation error:", exc.errors())
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=5000)
    



