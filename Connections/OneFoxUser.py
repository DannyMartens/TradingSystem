import json
import time
import threading
from websocket import create_connection
from websocket import _exceptions


class OneFoxUser(object):

    def __init__(self):
        """ Constructor
        :type interval: int
        :param interval: Check interval, in seconds
        """
        self.start = False
        self.current_time = 0
        self.currency = {}
        self.price = 0
        self.bid = 0
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    def run(self):
        """ Method that runs forever """
        ws = create_connection("wss://wsv1.1fox.com")
        ws.settimeout(15)
        result = "{\"id\": \"USER_8578\"}"
        self.current_time = time.time()
        while True:
            if not self.start:
                starting = json.dumps({
                            "operation": "subscribe",
                            "channel": "NONE"})
                ws.send(starting)
                self.start = True
                print("Sent Subscribe")
                print(ws.recv())
            if self.current_time + 15 < (time.time()):
                self.current_time = time.time()
                ws.send(json.dumps({
                    "operation": "keepalive"
                }))
                print("send stay alive -- time")
            try:
                if self.currency:
                    self.currency.clear()
                result = ws.recv()
            except _exceptions.WebSocketTimeoutException:
                ws.send(json.dumps({
                    "operation": "keepalive"
                }))
                print("send stay alive")
            self.currency = json.loads(result)
            time.sleep(.1)

    def get_update(self):
        if self.currency:
            return True
        else:
            return False
