from Logic import BitmexPrice, OneFoxPrice
from Connections import OneFoxThread
import requests

''' 
            -------------- LOGIC -----------------
            1) Find Difference between Bitmex and 1Fox bid's and ask's
            2) Bitmex's last trade is higher than 1Fox's ask's by 5%
                2A) Buy on 1Fox at market. Set Limit at last trade.
            -------------- LOGIC -----------------
                # 1Fox market buy fee == 0.04%
                # 1fox market sell fee == 0.00% (limit)
'''


class ComparePrice:
    def __init__(self, bitmex: float, onefox: float, fox_bid: float):
        self.bitmex_price = bitmex
        self.fox_price = onefox
        self.url = 'https://1fox.com/api/v1/'
        self.token = None
        self.position = None
        self.buy_price = None
        self.limit_order_id = None
        self.margin = 0.001
        self.leverage = 2
        self.fox_bid = fox_bid
        self.low_limit_id = 0
        self.trade = False

    def is_profitable(self):
        self.evaluate_market_trade()
        # self.place_low_limit_buy()

    def price_difference(self) -> float:
        return self.bitmex_price - self.fox_price

    def evaluate_market_trade(self):
        if self.fox_price != 0:
            if self.bitmex_price > (self.fox_price + 4) and self.calculate_slippage():
                if not self.trade:
                    print("doing trade------------------------------------------")
                    self.do_onefox_trade('market', self.bitmex_price)
                    self.trade = True
                    # todo: add deadman's switch
                else:
                    # this is where we want to check to amend price
                    if self.check_underwater_buy():
                        self.update_limit_sell()
                        print("updated profit take")
                    print("open trade")
            if self.fox_bid > (self.bitmex_price + 8) and self.calculate_slippage_short():
                if not self.trade:
                    print("doing trade------------------------------------------SHORT")
                    self.do_onefox_short(self.bitmex_price)
                    self.trade = True
                    # todo: add deadman's switch
                # else:
                #     # this is where we want to check to amend price
                #     if self.check_amend_price() and self.check_underwater_buy():
                #         self.update_limit_sell()
                    print("open trade")

    def do_onefox_trade(self, order_type: str, price: float):
        # amount to trade = margin

        self.fox_market_buy(self.margin, self.leverage)
        # self.fox_limit_sell(price, self.margin, self.leverage)
        self.get_execute_price(self.position)

    def do_onefox_short(self, price: float):
        self.fox_market_sell(self.margin, self.leverage)
        self.get_execute_price(self.position)

    def fox_market_sell(self, margin: float, leverage: int):
        current_url = self.fox_url()
        current_url += '&margin='
        current_url += str(margin)
        current_url += '&direction=SELL'
        current_url += '&leverage='
        current_url += str(leverage)
        current_url += '&order_type=MARKET'
        current_url += '&take_profit='
        current_url += str(self.bitmex_price)
        # print(current_url)
        r = requests.get(current_url)
        r = r.json()
        r = r.get('response')
        self.position = r.get('position_id')
        print(f'Position ID = {self.position}')  # should return int

    def fox_market_buy(self, margin: float, leverage: int):
        current_url = self.fox_url()
        current_url += '&margin='
        current_url += str(margin)
        current_url += '&direction=LONG'
        current_url += '&leverage='
        current_url += str(leverage)
        current_url += '&order_type=MARKET'
        current_url += '&take_profit='
        current_url += str(self.bitmex_price)
        # print(current_url)
        r = requests.get(current_url)
        r = r.json()
        r = r.get('response')
        self.position = r.get('position_id')
        print(f'Position ID = {self.position}')

    def fox_limit_sell(self, price: float, margin, leverage):
        current_url = self.fox_url()
        current_url += '&margin='
        current_url += str(margin)
        current_url += '&direction=SHORT'
        current_url += '&leverage='
        current_url += str(leverage)
        current_url += '&order_type=LIMIT'
        current_url += '&limit_price='
        current_url += str(price)
        r = requests.get(current_url)
        r = r.json()
        r = r.get('response')
        self.limit_order_id = r.get('order_id')

    def fox_url(self)-> str:
        url = self.url
        url += 'order/create.php?token='
        url += self.token
        url += '&symbol=BTCUSD'
        return url


    def open_trade(self)-> bool:
        r = requests.get(f'https://1fox.com/api/v1/position/trades.php?token={self.token}&position_id={self.position}')
        r = r.json()
        r = r.get('response')
        if not r:
            # list is empty - > no trade open currently
            return False
        else:
            return True

    def check_amend_price(self):
        r = requests.get('https://1fox.com/api/v1/user/overview.php?token'
                         '=None&pretty=true&currency=BTC')
        r = r.json()
        r = r.get('response')
        r = r.get('positions')
        if not r:
            # list is empty
            return True
        else:
            return False


    def calculate_slippage(self):
        r = requests.get("https://1fox.com/api/v1/market/slippage.php?pretty=true&symbol=BTCUSD&type=BUY&volume=0.001")
        r = r.json()
        price = r.get('response')
        price = price.get('price')
        price = float(price)
        # fee_price = 0.01 * 0.04
        # price = price + fee_price
        if price < self.bitmex_price:
            return True
        else:
            print("slippage is to high")
            return False

    def calculate_slippage_short(self):
        r = requests.get("https://1fox.com/api/v1/market/slippage.php?pretty=true&symbol=BTCUSD&type=SELL&volume=0.001")
        r = r.json()
        price = r.get('response')
        price = price.get('price')
        price = float(price)
        # fee_price = 0.01 * 0.04
        # price = price + fee_price
        if price > self.bitmex_price:
            return True
        else:
            print("slippage is to high")
            return False

    def get_execute_price(self, position_id):
        current_url = "https://1fox.com/api/v1/position/trades.php?token="
        current_url += self.token
        current_url += "&position_id="
        current_url += position_id
        r = requests.get(current_url)
        r = r.json()
        self.buy_price = r['response'][0].get("price")
        print(self.buy_price)

    def update_limit_sell(self):
        #  cancel order
        # self.cancel_order()
        # set new order with updated price.
        # self.fox_limit_sell(price=self.bitmex_price, margin=self.margin, leverage=self.leverage)
        # https://1fox.com/api/v1/order/create.php?token=YOUR_API_TOKEN&pretty=true&symbol=BTCUSD&margin=2.345&direction=SHORT&leverage=2&order_type=LIMIT&limit_price=4300.35&stop_loss=4200.50&take_profit=10000
        current_url = 'https://1fox.com/api/v1/position/edit.php?token=NONE&position_id='
        current_url += self.position
        current_url += '&take_profit='
        current_url += self.bitmex_price
        requests.get(current_url)

    def check_underwater_buy(self):
        if self.buy_price + 5 > self.bitmex_price and self.fox_bid >= self.bitmex_price:
            self.cancel_order()
            current_url = self.fox_url()
            current_url += '&margin='
            current_url += str(self.margin)
            current_url += '&direction=SHORT'
            current_url += '&leverage='
            current_url += str(self.leverage)
            current_url += '&order_type=MARKET'
            # print(current_url)
            r = requests.get(current_url)
            r = r.json()

    def cancel_order(self):
        current_url = "https://1fox.com/api/v1/order/close.php?token=NONE&order_id="
        current_url += self.limit_order_id
        requests.get(current_url)

    def calculate_limit_order(self):
        pass

    # def place_low_limit_buy(self):
    #     # Idea: place buy limit order $15 under bid.
    #     # If hit place sell $5 under bid
    #     if self.fox_price != 0:
    #         current_url = self.fox_url()
    #         current_url += '&margin='
    #         current_url += str(self.margin)
    #         current_url += '&direction=BUY'
    #         current_url += '&leverage='
    #         current_url += str(self.leverage)
    #         current_url += '&order_type=LIMIT'
    #         current_url += '&limit_price='
    #         current_url += str(self.fox_bid - 15)
    #         current_url += '&take_profit='
    #         current_url += str(self.fox_bid - 5)
    #         print(current_url)
    #         r = requests.get(current_url)
    #         r = r.json()
    #         r = r.get('response')
    #         self.low_limit_id = r.get('order_id')

    '''
    
        symbol	            string	                Market symbol.
        margin	            float	                Margin (also called "amount" in the user interface) of the order. Gets rounded down to the best possible value to buy/sell an integral number of contracts.
        direction	        string	                Direction of the order - either "LONG" or "SHORT".
        leverage	        positive integer	    Value denoting the leverage used for this order.
        order_type	        string	                Type of the order - either market ("MARKET"), limit ("LIMIT") or stop entry ("STOP_ENTRY").
        limit_price	        float	                Limit price to be used when opening the order as a limit order - otherwise this parameter will not be used.
        stop_entry_price	float	                Stop entry price to be used when opening the order a stop entry order - otherwise this parameter will not be used.
        stop_loss	        float (optional)	    Stop loss limit for the order, once it has been opened.
        take_profit	        float (optional)	    Take profit price for the order, once it has been opened.
        post_only	        boolean (optional)	    Placing a post-only order will fail if it would match with a pre-existing order. (Default: false)
        referral_id	        string (optional)	    You can override the user's referral_id with this parameter. Only applies for this order/position. An account cannot refer itself.
            
    '''