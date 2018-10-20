#!/usr/bin/python

# ~~~~~==============   HOW TO RUN   ==============~~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py; sleep 1; done

from __future__ import print_function

import sys
import socket
import json
import time

# ~~~~~============== CONFIGURATION  ==============~~~~~
# replace REPLACEME with your team name!
team_name="CZADOWECHLOPAKI"
# This variable dictates whether or not the bot is connecting to the prod
# or test exchange. Be careful with this switch!
test_mode = True

# This setting changes which test exchange is connected to.
# 0 is prod-like
# 1 is slower
# 2 is empty
test_exchange_index=0
prod_exchange_hostname="production"

port=25000 + (test_exchange_index if test_mode else 0)
exchange_hostname = "test-exch-" + team_name if test_mode else prod_exchange_hostname

# ~~~~~============== NETWORKING CODE ==============~~~~~
def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((exchange_hostname, port))
    return s.makefile('rw', 1)

def write_to_exchange(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

def read_from_exchange(exchange):
    return json.loads(exchange.readline())

# ~~~~~============== OPERATIONS =============~~~~~
PORTFOLIO = {}
BUYS = {}
SELLS = {}

def buy_bond(exchange, price, size, order_id):
    obj = {"type": "add", "order_id": order_id, "symbol": "BOND", "dir": "BUY", "price": price, "size": size}
    json.dump(obj, exchange)
    exchange.write("\n")

def sell_bond(exchange, price, size, order_id):
    obj = {"type": "add", "order_id": order_id, "symbol": "BOND", "dir": "SELL", "price": price, "size": size}
    json.dump(obj, exchange)
    exchange.write("\n")

# ~~~~~============== helpers ==============~~~~~

def getId(previous_id):
    t = time.time()
    if t - previous_id < 1.5:
        time.sleep(1)
    return int(time.time())

# ~~~~~============== MAIN LOOP ==============~~~~~

def main():
    LAST_ORDER_ID = int(time.time())
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    hello_from_exchange = read_from_exchange(exchange)
    # Initialize portfolio
    for symbol in hello_from_exchange["symbols"]:
        PORTFOLIO[symbol['symbol']] = symbol["position"]
        BUYS[symbol['symbol']] = []
        SELLS[symbol['symbol']] = []
    #go!
    while(True):
        response = read_from_exchange(exchange)
        if response["type"] == "book":
            symbol = response["symbol"]
            print(symbol)
            BUYS[symbol] = response["buy"]
            SELLS[symbol] = response["sell"]
            print(symbol, len(BUYS[symbol]), len(SELLS[symbol]))
            
        #time.sleep(1)
			
    # A common mistake people make is to call write_to_exchange() > 1
    # time for every read_from_exchange() response.
    # Since many write messages generate marketdata, this will cause an
    # exponential explosion in pending messages. Please, don't do that!

if __name__ == "__main__":
    main()
