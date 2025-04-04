import httpx

import orjson as json

from typing import Any
from fastapi import WebSocket


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


async def resp(ws:WebSocket, code:int, msg:str)->None:
    await ws.send_text(str(json.dumps(
        {'ret_code': code, 'msg': msg}
            )))
