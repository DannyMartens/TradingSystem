from Logic import BitmexPrice, OneFoxPrice
from Connections import OneFoxThread
import requests


class UpdatedBid:
    def __init__(self, bitmex: float, fox_bid: float, fox_ask: float, fox_update: bool):
        self.bitmex_price = bitmex
        self.fox_ask = fox_ask
        self.fox_bid = fox_bid
        self.fox_update = fox_update
        self.stop_loss_buy = (self.fox_bid - 15)
        self.stop_loss_short = (self.fox_ask + 15)
        self.token = 'NONE'
        self.low_bid = 0
        self.amount = 0.001
        self.leverage = 2
        self.response = None
        self.order_id = None
        self.position_type = None

    def run(self):
        if not self.check_open():
            if self.buy_rule_check(self.fox_bid):
                self.place_buy_order()
            elif self.sell_rule_check(self.fox_ask):
                self.place_sell_order()
        else:
            self.rule_update()
            # have open order out.

    def buy_rule_check(self, fox_bid):
        if fox_bid + 15 < self.bitmex_price:
            return True
        else:
            return False

    def sell_rule_check(self, fox_ask):
        if fox_ask - 15 > self.bitmex_price:
            return True
        else:
            return False

    def place_buy_order(self):
        response = self.place_order(limit_price=str(self.fox_bid + 1), take_profit=str(self.bitmex_price),
                                    amount=str(self.amount),
                                    leverage=str(self.leverage),
                                    direction='LONG', stop_loss=str(self.stop_loss_buy))
        self.order_id = response.get("order_id")
        self.position_type = 'Long'

    def place_sell_order(self):
        response = self.place_order(limit_price=str(self.fox_ask - 1), take_profit=str(self.bitmex_price),
                                    amount=str(self.amount),
                                    leverage=str(self.leverage),
                                    direction='SHORT', stop_loss=str(self.stop_loss_short))
        self.order_id = response.get("order_id")
        self.position_type = 'Short'

    def place_order(self, limit_price: str, take_profit: str, amount: str, leverage: str,
                    direction: str, stop_loss: str):

        url = self.url_generator_orders(amount=amount, direction=direction, leverage=leverage, order_type='LIMIT',
                                        limit_price=limit_price, take_profit=take_profit, stop_loss=stop_loss)
        print(url)
        r = self.send_request(url)
        return r.get('response')

    def check_open(self):
        if self.fox_update:
            positions = self.user_get_positions()
            if positions:
                return True
            else:
                return False

    def rule_update(self):
        orders = self.user_get_orders()
        orders_keys = list(orders.keys())
        all_orders_price = []
        if orders:
            for x in orders_keys:
                all_orders_price.append(orders.get(x).get("price"))

        all_orders_price = sorted(all_orders_price, key=int)
        level = 0
        for order in all_orders_price:
            pass


    def check_update(self, current_price: float, level: int):
        orderbook = self.send_request("https://1fox.com/api/v1/market/orderbook.php?symbol=BTCUSD&depth=3")
        orderbook = orderbook.get("response")
        if self.position_type == 'Long':
            orderbook_bids: list = orderbook.get("bids") # list of dicts
            for x in orderbook_bids:
                if self.buy_rule_check(x.get("price")):
                    pass  # TODO: update
        elif self.position_type == 'Short':
            orderbook_asks: list = orderbook.get("bids") # list of dicts

    def update_order(self):
        r = self.send_request(
            "https://1fox.com/api/v1/order/close.php?token=NONE&order_id=" +
            self.order_id)

    def user_get_positions(self) -> dict:
        r = self.send_request("https://1fox.com/api/v1/user/overview.php?"
                              "token=NONE&currency=BTC")
        r = r.get("response")
        r = r.get("positions")
        return r

    def user_get_orders(self) -> dict:
        r = self.send_request("https://1fox.com/api/v1/user/overview.php?"
                              "token=NONE&currency=BTC")
        r = r.get("response")
        r = r.get("orders")
        return r

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
