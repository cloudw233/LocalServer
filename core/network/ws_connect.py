import traceback

import httpx
import loguru
import orjson as json

from fastapi import WebSocket

from core.builtins.elements import AccountElements
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
    while True:
        recv_data = dict(await websocket.receive()).get("bytes").decode("utf-8")
        logger.debug(recv_data)
        recv_data = json.loads(recv_data)
        msgchain = MessageChainD(recv_data)
        msgchain.serialize()
        msgchain_data = msgchain.messages
        usrname, action, verified = msgchain_data[0].username, msgchain_data[0].action, (await msgchain_data[0].verify())
        if (not verified) and action == "register":
            await msgchain_data[0].register()
            logger.debug("Registering user: "+usrname)
            verified = True
            await resp(websocket, 0, "Successfully registered", "register")
        if verified:pass
        else:
            return
        try:
            if verified:
                pool[pool_name][usrname] = websocket
            else:
                del pool[pool_name][usrname]
                break
            match action:
                case "data":
                    logger.debug(msgchain_data)
                    match pool_name:
                        case "sensor":
                            for connection in [pool["client"], pool["monitor"]]:
                                if connection.get(usrname):
                                    await connection[usrname].send_text(json.dumps(msgchain.deserialize()).decode("utf-8"))
                        case "client":
                            if pool["sensor"].get(usrname):
                                await pool["sensor"][usrname].send_text(json.dumps(msgchain.deserialize()).decode("utf-8"))
                            response = await process_message(httpx_client, msgchain)
                            await websocket.send_text(json.dumps(response.deserialize()).decode("utf-8"))
                case "login":
                    logger.info("Login successful: "+ usrname)
                    await resp(websocket, 0, "Login successful", 'login')
        except Exception as e:
            del pool[pool_name][usrname]
            await websocket.close()
            logger.error(e)
            traceback.print_exc()
            break
