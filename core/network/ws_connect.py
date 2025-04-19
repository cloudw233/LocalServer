import httpx
import loguru

from fastapi import WebSocket

from core.builtins.message_constructors import MessageChainD, process_message
from pydantic_core import from_json
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
                del pool[pool_name][usrname]
                break
            if action == "data":
                logger.debug(msgchain)
                message_lst = []
                await resp(websocket, 0, "Data received")
                await process_message(httpx_client, message_lst, msgchain)
                for connection in [pool["client"], pool["monitor"]]:
                    if connection.get(usrname):
                        await connection[usrname].send_text(msgchain.deserialize())
            if action == "login":
                await resp(websocket, 0, "Login successful")
                await pool["sensor"][usrname].send_text(msgchain.deserialize())
            if action == "register":
                await resp(websocket, 0, "Register successful")
                await pool["sensor"][usrname].send_text(msgchain.deserialize())
        except Exception as e:
            del pool[pool_name][usrname]
            logger.error(e)
