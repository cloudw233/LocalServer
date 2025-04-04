import loguru
import orjson as json

from fastapi import WebSocket
from core.database.models import User
from core.pydantic_models import *
from pydantic_core import from_json
from core.utils.http import resp

async def switch_data(
        pool: dict, 
        websocket: WebSocket, 
        logger: loguru._logger.Logger,
        account: Account, 
        users: User) -> None:
    """
    从服务端和客户端之间接收和发送数据
    :param pool: 连接池
    :param websocket: ws连接类
    :param logger: 日志类
    :param account: 账户模型
    :param users: 用户数据库
    :return:
    """
    await websocket.accept()
    while True:
        try:
            data = await websocket.receive_text()
            _account = account.model_validate(from_json(data, allow_partial=True))
            usrname = _account.username
            action = _account.action
            match action:
                case 'register':
                    usr, is_created = await users.get_or_create(username=usrname)
                    if is_created:
                        usr.password = _account.password
                        await resp(websocket, 0, 'Successfully Registered')
                    else:
                        await resp(websocket, 1, 'Account Already Exists')
                case 'login':
                    user = await users.get_or_none(username=usrname)
                    if user:
                        verified = await user[0].verify(_account.password)
                        if verified:
                            pool[usrname] = websocket
                            _resp = await websocket.receive_text()
                            logger.debug(_resp)
                        else:
                            await resp(websocket, 0, 'Password Error')
                    else:
                        await resp(websocket, 1, 'Account Not Exists')
            logger.debug(data)

        except Exception as e:
            logger.error(e)

async def switch_heart_data(
        client_pool: dict, 
        monitor_pool:dict, 
        heart_pool:dict, 
        websocket: WebSocket, 
        logger: loguru._logger.Logger,
        account: Account,
        heart: Heart, 
        users: User) -> None:
    """
    从服务端和客户端之间接收和发送数据
    :param client_pool: 客户端连接池
    :param monitor_pool: 监控端连接池
    :param heart_pool: 心率连接池
    :param websocket: ws连接类
    :param logger: 日志类
    :param heart: 心率模型
    :param users: 用户数据库
    :return:
    """
    await websocket.accept()
    while True:
        try:
            data = await websocket.receive_text()
            _bpm = heart.model_validate(from_json(data, allow_partial=True))
            usrname = _bpm.username
            action = _bpm.action
            match action:
                case 'data':
                    heart_pool[usrname] = websocket
                    logger.debug(_bpm)
                    await websocket.send_text(str(json.dumps({'ret_code': 0})))
                    for connection in [client_pool, monitor_pool]:
                        if connection.get(usrname):
                            await client_pool[usrname].send_text(data)

        except Exception as e:
            logger.error(e)