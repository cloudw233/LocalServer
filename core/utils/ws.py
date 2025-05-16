from starlette.websockets import WebSocket


async def get_ws_data(ws: WebSocket):
    __data = dict(await ws.receive())
    if __data.get('bytes'):
        return __data.get('bytes').decode('utf-8')
    return __data.get('text')