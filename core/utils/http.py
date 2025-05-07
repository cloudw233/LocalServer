import httpx

import orjson as json

from typing import Any

from typing import Literal
from fastapi import WebSocket
from loguru import logger

from core.builtins.assigned_element import ResponseElement


async def url_post(client: httpx.AsyncClient, url: str, data: dict|str, headers: dict = None) -> Any:
    """
    :param client: httpx.AsyncClient
    :param url: 链接
    :param data: 数据
    :param headers: 请求头
    :return: 返回请求结果
    """
    response = await client.post(url, data=data, headers=headers, follow_redirects=True)
    return response.text

async def url_get(client: httpx.AsyncClient, url: str, headers: dict|str = None) -> Any:
    """
    :param client: httpx.AsyncClient
    :param url: 链接
    :param headers: 请求头
    :return: 返回请求结果
    """
    response = await client.get(url, headers=headers, follow_redirects=True)
    return response.text


async def resp(ws:WebSocket, code: Literal[0,1,2], msg:str, flag:Any) -> list:
    """
    构建返回消息并发送
    :param ws: websocket连接
    :param code: 返回值，0:成功，1:警告，2:错误
    :param msg: 返回消息
    :param flag: 标志
    :return: 返回消息
    """
    __message = [{"meta": 'ResponseElement', "data": ResponseElement(ret_code=code, message=msg, flag=flag).dump()}]
    await ws.send_text(json.dumps(__message).decode("utf-8"))
    logger.debug(f"Send message: {__message}")
