import orjson as json

import loguru, uvicorn, logging, httpx

from fastapi import FastAPI, APIRouter, WebSocket
from pydantic_core import from_json
from contextlib import asynccontextmanager

from core.database.models import User
from core.pydantic_models import *
from core.utils.ws_connect import switch_data, switch_heart_data

from extensions.weather import QWeather
from extensions.deepseek import get_deepseek_anwser

from core.database import init_db

httpx_client = httpx.AsyncClient()

sensor_pool = {}
client_pool = {}
monitor_pool = {}
heart_pool = {}

logger = loguru.logger


@asynccontextmanager
async def httpx_c(app: FastAPI):
    await init_db()
    yield
    await httpx_client.aclose()


app = FastAPI(lifespan=httpx_c)



# @app.websocket("/sensor")
# async def sensor(websocket: WebSocket):
#     await websocket.accept()
#     while True:
#         data = await websocket.receive_text()
#         logger.debug(data)
#         try:
#             _sensor = Sensor.model_validate(from_json(data, allow_partial=True))
#             usrname = _sensor.username
#             if _sensor.action == 'data':
#                 sensor_pool[usrname] = websocket
#                 logger.debug(_sensor)
#                 await websocket.send_text(str(json.dumps({'ret_code': 0})))
#                 for connection in [client_pool, monitor_pool]:
#                     if connection.get(usrname):
#                         await client_pool[usrname].send_text(data)
#
#         except Exception as e:
#             logger.error(e)
#
#
# @app.websocket("/client")
# async def client(websocket: WebSocket):
#     await switch_data(client_pool, websocket, logger, Account, User)
#
#
# @app.websocket("/monitor")
# async def monitor(websocket: WebSocket):
#     await switch_data(monitor_pool, websocket, logger, Account, User)
#
# @app.websocket("/heart")
# async def heart(websocket: WebSocket):
#     await switch_heart_data(client_pool, monitor_pool, heart_pool, websocket, logger, Account, Heart, User)

@app.post("/api/weather/7days")
async def weather_(weather: Weather):
    __city = weather.city
    __weather = QWeather(__city, httpx_client)
    return await __weather.get_7days()

@app.post("/api/weather/indices")
async def indices(weather: Weather):
    __city = weather.city
    __weather = QWeather(__city, httpx_client)
    return await __weather.get_indices()

@app.post("/api/weather/aqi")
async def aqi(weather: Weather):
    __city = weather.city
    __weather = QWeather(__city, httpx_client)
    return await __weather.get_aqi()

@app.post("/api/weather/city")
async def city(weather: Weather):
    __city = weather.city
    __weather = QWeather(__city, httpx_client)
    return await __weather.find_city()

@app.post("/api/deepseek")
async def deepseek(deepseek: DeepSeek):
    question = deepseek.question
    return await get_deepseek_anwser(question)
     
    


if __name__ == "__main__":
    try:
        class InterceptHandler(logging.Handler):
            def emit(self, record):
                logger_opt = logger.opt(depth=6, exception=record.exc_info)
                logger_opt.log(record.levelno, record.getMessage())


        def init_logger():
            LOGGER_NAMES = ("uvicorn", "uvicorn.access",)
            for logger_name in LOGGER_NAMES:
                logging_logger = logging.getLogger(logger_name)
                logging_logger.handlers = [InterceptHandler()]


        config = uvicorn.Config(app, host="0.0.0.0", port=int(55433), access_log=True, workers=2)
        server = uvicorn.Server(config)
        init_logger()
        server.run()
    except KeyboardInterrupt:
        del client_pool
        del sensor_pool
        del monitor_pool
