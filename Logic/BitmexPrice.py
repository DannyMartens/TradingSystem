from Connections import BitmexConnection
import logging
from time import sleep


class Bitmex:
    def __init__(self, endpoint, symbol, api_key, api_secret):
        self.ws = BitmexConnection.BitMEXWebsocket(endpoint=endpoint, symbol=symbol,
                                              api_key=api_key,
                                              api_secret=api_secret)
        self.last_ask: float = 0
        self.last_bid: float = 0
        self.last_trade: float = 0

    def run(self):
        self.ws.get_instrument()  # needed to avoid error.

    def get_bitmex_price(self):
        bmex_ticker = self.ws.get_ticker()
        self.last_ask = bmex_ticker['sell']
        self.last_bid = bmex_ticker['buy']
        self.last_trade = bmex_ticker['last']
        return self.last_trade

    def stop(self):
        return self.ws.exit()
