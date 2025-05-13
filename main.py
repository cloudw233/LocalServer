import loguru, uvicorn, logging, httpx

from fastapi import FastAPI, WebSocket
from contextlib import asynccontextmanager

from core.pydantic_models import *

from extensions.weather import QWeather
from extensions.deepseek import get_deepseek_anwser

from core.database import init_db
from core.network.ws_connect import switch_data

httpx_client = httpx.AsyncClient(verify=False)

connection_pool = {
    "client": {},
    "sensor": {},
    "monitor": {},
}

logger = loguru.logger


@asynccontextmanager
async def httpx_c(app: FastAPI):
    await init_db()
    yield
    await httpx_client.aclose()


app = FastAPI(lifespan=httpx_c)


@app.websocket("/sensor")
async def sensor(websocket: WebSocket):
    await switch_data(connection_pool, 'sensor', websocket, httpx_client, logger)


@app.websocket("/client")
async def client(websocket: WebSocket):
    await switch_data(connection_pool, 'client', websocket, httpx_client, logger)


@app.websocket("/monitor")
async def monitor(websocket: WebSocket):
    await switch_data(connection_pool, 'monitor', websocket, httpx_client, logger)


@app.post("/api/weather/7days")
async def weather_(weather: Weather):
    __city = weather.city
    __weather = QWeather(httpx_client, __city)
    return await __weather.get_7days()


@app.post("/api/weather/indices")
async def indices(weather: Weather):
    __city = weather.city
    __weather = QWeather(httpx_client, __city)
    return await __weather.get_indices()


@app.post("/api/weather/aqi")
async def aqi(weather: Weather):
    __city = weather.city
    __weather = QWeather(httpx_client, __city)
    return await __weather.get_aqi()


@app.post("/api/weather/city")
async def city(weather: Weather):
    __city = weather.city
    __weather = QWeather(httpx_client, __city)
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
        del connection_pool
