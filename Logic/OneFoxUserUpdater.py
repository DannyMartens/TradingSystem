from Connections import OneFoxUser


class OneFoxUpdate:
    def __init__(self, endpoint, symbol):
        self.end = endpoint
        self.symbol = symbol
        # self.ws = OneFoxWS.OneFoxWebSocket()
        self.ws = OneFoxUser.OneFoxUser()
        # self.conn = OneFoxWS.Connector()

    def run(self):
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(self.conn.run())
        # def stop(self):
        #     return self.ws.exit()
        pass

    def get_update(self):
        return self.ws.get_update()

