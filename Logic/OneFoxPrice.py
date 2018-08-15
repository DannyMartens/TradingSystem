from Connections import OneFoxWS, OneFoxThread
import asyncio
import websockets


class OneFox:
    def __init__(self, endpoint, symbol):
        self.end = endpoint
        self.symbol = symbol
        # self.ws = OneFoxWS.OneFoxWebSocket()
        self.ws = OneFoxThread.OneFoxThread()
        # self.conn = OneFoxWS.Connector()

    def run(self):
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(self.conn.run())
        # def stop(self):
        #     return self.ws.exit()
        pass

    def get_price(self):
        return self.ws.get_price()

    def get_bid(self):
        return self.ws.get_bid()
