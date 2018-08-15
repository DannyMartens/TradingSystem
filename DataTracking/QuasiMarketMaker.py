from Logic import BitmexPrice, OneFoxPrice
from Connections import OneFoxThread
import requests

''' 
Doesn't really work and deprecated for a better idea in Updated Bid Holder or DataHolder. 
'''

# if not then put it on that level.

class ImpliedMarkets:
    def __init__(self, bitmex: float, fox_bid: float, fox_ask: float):
        self.bitmex_price = bitmex
        self.fox_ask = fox_ask
        self.fox_bid = fox_bid
        self.token = 'NONE'
        self.position = None
        self.low_bid = 0

    def run(self):
        if self.fox_bid != 0:
            self.low_bid = self.get_orderbook_bid()
            self.check_rules_long()

    def check_rules_long(self) -> bool:
        if self.order_check() and self.ask_rule() and self.bid_rule():
            print("BUYING SOMETHING AHHHHH")
            # for buy only
            # qualifies for putting a bid
            bid = self.low_bid + 1
            ask = self.fox_ask - 1
            amount = 0.001
            leverage = 2
            stop_loss = bid - 20
            self.place_order(limit_price=str(bid), take_profit=str(ask), amount=str(amount), leverage=str(leverage),
                             direction='LONG', stop_loss=str(stop_loss))

        else:
            pass
            # do nothing.

    def bid_rule(self) -> bool:
        # RULE: 10 points less then bitmex
        print(f'self.low_bid + 10 >= self.bitmex_price {self.fox_bid + 10 >= self.bitmex_price} and self.low_bid + 5 = {self.low_bid + 5} > self.fox_bid={self.fox_bid}  {self.low_bid + 5 <= self.fox_bid } ')
        if self.low_bid + 10 >= self.bitmex_price and self.low_bid + 5 <= self.fox_bid:
            # set limit buy 1 point higher than current bid
            return True
        else:
            return False

    def ask_rule(self) -> bool:
        print(f'self.fox_ask >= self.low_bid + 8 == {self.fox_ask >= (self.low_bid + 8)}')
        if self.fox_ask >= self.low_bid + 8:
            return True
        else:
            return False

    def order_check(self):
        if not self.check_open(self.position):
            #no open trade right now. Valid to place a order
            return True
        else:

            return False
        # checks to see if there is an order already placed.
        # if there is check to see if it is still the highest in the orderbook
        # and confides to the rules otherwise cancel.
        # if it is not the highest in the order book check rules then amend.

    def place_order(self, limit_price: str, take_profit: str, amount: str, leverage: str,
                    direction: str, stop_loss: str):

        url = self.url_generator_orders(amount=amount, direction=direction, leverage=leverage, order_type='LIMIT',
                                        limit_price=limit_price, take_profit=take_profit, stop_loss=stop_loss)
        print(url)
        r = self.send_request(url)
        r = r.get('response')
       # self.position = r.get('position_id')

    def check_open(self, position_id):
        url = 'https://1fox.com/api/v1/position/trades.php?token=NONE&position_id='
        url += str(position_id)  # position id from user/transactions.php
        r = self.send_request(url)
        if not r.get('response'):
            # can not be found. Means that the order has been closed and there is no open order at the moment.
            return False
        else:
            return True

    def update_order(self):
        # cancel and put up bid again.
        pass

    @staticmethod
    def url_generator_orders(amount, direction, leverage, order_type, limit_price, take_profit, stop_loss):
        url_list = ['https://1fox.com/api/v1/order/create.php?token=NONE&symbol=BTCUSD',
                    '&margin=', amount, '&direction=', direction, '&leverage=', leverage, '&order_type=', order_type,
                    '&limit_price=', limit_price, '&take_profit=', take_profit, '&stop_loss=', stop_loss]
        generator = [sub for sub in url_list]
        return ''.join(generator)

    @staticmethod
    def send_request(url) -> dict:
        r = requests.get(url)
        r = r.json()
        return r

    def get_orderbook_bid(self) -> float:
        r = self.send_request("https://1fox.com/api/v1/market/orderbook.php?symbol=BTCUSD&depth=2")
        response = r.get('response')
        bid: list = response.get('bids')
        bid = bid[1].get('price')
        # ask: list = response.get('asks')
        return float(bid)