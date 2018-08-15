import websockets
from websockets import connect
import json
import asyncio
import time

# Deprecated for threading instead.


class OneFoxWebSocket:
    async def __aenter__(self):
        self._conn = connect("wss://wsv1.1fox.com")
        self.websocket = await self._conn.__aenter__()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self._conn.__aexit__(*args, **kwargs)

    async def send(self, message):
        await self.websocket.send(message)

    async def receive(self):
        return await self.websocket.recv()


class Connector:
    def __init__(self):
        self.list_price = []

    async def main(self):
        async with OneFoxWebSocket() as websocket:
            name = (json.dumps({
                "operation": "subscribe",
                "channel": "TICKER_BTCUSD"
            }))
            print("sent item")
            await websocket.send(name)
            greeting = await websocket.receive()
            # self.list_price.append(greeting)
            print(f"< {greeting}")
            current_time = time.time()
            # while True:
            try:
                temp_ct = current_time
                temp_time = time.time()
                if current_time + 25 < (time.time()):
                    current_time = time.time()
                    await websocket.send(json.dumps({
                        "operation": "keepalive"
                    }))
                    print("send stay alive")
                price: dict = await asyncio.wait_for(websocket.receive(), timeout=20)
                price = json.loads(price)
            except asyncio.TimeoutError:
                # No data in 20 seconds, check the connection.
                try:
                    await websocket.send(json.dumps({
                        "operation": "keepalive"
                    }))
                except asyncio.TimeoutError:
                    # No response to ping in 10 seconds, disconnect.
                    pass
            else:
                print(price)
                if price.get("id") == 'TICKER_BTCUSD':
                    self.list_price.append(price['data']['ask'])

    def get_price(self):
        if self.list_price:
            return self.list_price[-1]
        else:
            return 0

    async def run(self):
        while True:
            future = asyncio.ensure_future(self.main())

        print("done")