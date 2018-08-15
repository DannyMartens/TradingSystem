import logging
import time
import sys

from btfxwss import BtfxWss


class Connection:
    #     def __init__(self, key=None, secret=None, log_level=None, **wss_kwargs):
    def __init__(self, symbol):
        self.wss = BtfxWss(key=None,
                           secret=None,
                           addr='wss://api.bitfinex.com/ws/2')
        self.wss.start()
        self.symbol = symbol
        while not self.wss.conn.connected.is_set():
            time.sleep(1)
    
        self.wss.subscribe_to_ticker(symbol)
        self.wss.subscribe_to_order_book(symbol)

    def stop(self):
        # Unsubscribing from channels:
        # self.wss.unsubscribe_from_ticker('BTCUSD')
        # self.wss.unsubscribe_from_order_book('BTCUSD')

        # Shutting down the client:
        self.wss.stop()

    def get_bitfinex_price(self):
        ticker_q = self.wss.tickers(self.symbol)  # returns a Queue object for the pair.
        return ticker_q
