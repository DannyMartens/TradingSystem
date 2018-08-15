from Logic import BitmexPrice, OneFoxPrice
from Connections import OneFoxUser
from DataTracking import UpdatedBidHolder
import time

if __name__ == "__main__":
    bmex_connection = BitmexPrice.Bitmex(endpoint='wss://www.bitmex.com/realtime', symbol="XBTUSD",
                                         api_key="NONE",
                                         api_secret="NONE")

    oneFox_connection = OneFoxPrice.OneFox(endpoint="wss://wsv1.1fox.com", symbol="TICKER_BTCUSD")

    oneFox_user = OneFoxUser.OneFoxUser(endpoint="wss://wsv1.1fox.com", symbol="TICKER_BTCUSD")
    bmex_connection.run()
    # oneFox_connection.run()
    # initializes bmex

    # oneFox_connection.run()
    # Connects to 1Fox and sub's to trades to see the most recent call.

    # Running forever.
    while True:
        # Getting the most recent price from both bitmex and 1Fox.
        # Evaluating those prices and seeing which is higher.
        # Bitmex price = last trade price.
        # 1Fox Price = current asking price.
        # price = DataHolder.ComparePrice(bmex_connection.get_bitmex_price(), float(oneFox_connection.get_price()),
        #                                 float(oneFox_connection.get_bid()))
        # price.is_profitable()
        fox_ask = oneFox_connection.get_price()
        fox_bid = oneFox_connection.get_bid()
        bmex_price = bmex_connection.get_bitmex_price()
        fox_user = oneFox_user.get_update()
        # print(f'fox.ask = {fox_ask}, fox.bid = {fox_bid}, bmex = {bmex_price}')
        quasi = UpdatedBidHolder.UpdatedBid(fox_ask=float(fox_ask),
                                            fox_bid=float(fox_bid),
                                            bitmex=float(bmex_price),
                                            fox_update=fox_user)

        quasi.run()

        time.sleep(.1)
