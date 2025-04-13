from enum import verify

import loguru
import orjson as json

from fastapi import WebSocket
from core.database.models import User
from core.pydantic_models import *
from core.builtins.message_constructors import MessageChain, MessageChainD
from pydantic_core import from_json
from core.utils.http import resp

async def switch_data(
        pool: dict,
        pool_name: str,
        websocket: WebSocket, 
        logger: loguru._logger.Logger) -> None:
    """
    从服务端和客户端之间接收和发送数据
    :param pool_name: 池名称
    :param pool: 连接池
    :param websocket: ws连接类
    :param logger: loguru日志
    :return:
    """
    await websocket.accept()
    recv_data = await websocket.receive_text()
    logger.debug(recv_data)
    recv_data = from_json(recv_data, allow_partial=True)
    msgchain = MessageChainD(recv_data).serialize()
    usrname, action, verified = msgchain[0].username, msgchain[0].action, msgchain[0].verify()
    while True:
        try:
            if verified and usrname not in pool[pool_name]:
                pool[pool_name][usrname] = websocket
            else:
                await resp(websocket, 2, "Account verification failed")
                break
            if action == "data":
                logger.debug(msgchain)
                await resp(websocket, 0, "Data received")
                for connection in [pool["client"], pool["monitor"]]:
                    if connection.get(usrname):
                        await connection[usrname].send_text(msgchain.deserialize())
            if action == "login":
                await resp(websocket, 0, "Login successful")

        except Exception as e:
            del pool[pool_name][usrname]
            logger.error(e)