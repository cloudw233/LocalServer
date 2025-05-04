import traceback

import httpx
import loguru
import orjson as json

from fastapi import WebSocket

from core.builtins.message_constructors import MessageChainD, process_message
from core.utils.http import resp


async def switch_data(
        pool: dict,
        pool_name: str,
        websocket: WebSocket,
        httpx_client: httpx.AsyncClient,
        logger: loguru._logger.Logger) -> None:
    """
    从服务端和客户端之间接收和发送数据
    :param httpx_client:
    :param pool_name: 池名称
    :param pool: 连接池
    :param websocket: ws连接类
    :param logger: loguru日志
    :return:
    """
    await websocket.accept()
    recv_data = dict(await websocket.receive()).get("bytes").decode("utf-8").replace("\\", '')
    logger.debug(recv_data)
    recv_data = json.loads(recv_data)
    msgchain = MessageChainD(recv_data)
    msgchain.serialize()
    msgchain_data = msgchain.messages
    usrname, action, verified = msgchain_data[0].username, msgchain_data[0].action, (await msgchain_data[0].verify())
    while True:
        try:
            if verified and usrname not in pool[pool_name]:
                pool[pool_name][usrname] = websocket
            else:
                del pool[pool_name][usrname]
                break
            match action:
                case "data":
                    logger.debug(msgchain_data)
                    await process_message(httpx_client, msgchain)
                    for connection in [pool["client"], pool["monitor"]]:
                        if connection.get(usrname):
                            await connection[usrname].send_text(json.dumps(msgchain.deserialize()).decode("utf-8"))
                case "login":
                    await resp(websocket, 0, "Login successful", 'login')
                case "register":
                    await resp(websocket, 0, "Register successful", 'register')
        except Exception as e:
            del pool[pool_name][usrname]
            logger.error(e)
            traceback.print_exc()
            break
