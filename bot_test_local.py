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


def buy(exchange, price, size, symbol):
    obj = {"type": "add", "order_id": int(time.time()), "symbol": symbol, "dir": "BUY", "price": price, "size": size}
    json.dump(obj, exchange)
    exchange.write("\n")

def convert(exchange, size, symbol):
    obj = {"type": "convert", "order_id": int(time.time()), "symbol": symbol, "dir": "BUY", "size": size}
    json.dump(obj, exchange)
    exchange.write("\n")

def sell(exchange, price, size, symbol):
    obj = {"type": "add", "order_id": int(time.time()), "symbol": symbol, "dir": "SELL", "price": price, "size": size}
    json.dump(obj, exchange)
    exchange.write("\n")
    
def arbitrage_ADR(exchange):
    VALE_buy = get_price(symbol = "VALE", operation = 'buy')
    VALE_sell = get_price(symbol = "VALE", operation = 'sell')
    VALBZ_buy = get_price(symbol = 'VALBZ', operation = 'buy')
    VALBZ_sell = get_price(symbol = 'VALBZ', operation = 'sell')
    
    if VALBZ_buy > VALE_sell + 10:
        # Buy VALE
        buy(exchange, VALE_sell, 1, "VALE")
        # Convert to VALBZ
        convert(exchange, 1, "VALBZ", order_id)
        # Sell VALBZ
        sell(exchange, VALBZ_buy, 1, "VALBZ")
    if VALBZ_sell + 10 < VALE_buy:
        # Buy VALBZ
        buy(exchange, VALBZ_sell, 1, "VALBZ")
        # Convert to VALE
        convert(exchange, 1, "VALE")
        # Sell VALE
        sell(exchange, VALBE_buy, 1, "VALE")
        
# ~~~~~============== MAIN LOOP ==============~~~~~

def main():
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    hello_from_exchange = read_from_exchange(exchange)
    # Initialize portfolio
    i = 0
    while(True):
        response = read_from_exchange(exchange)
        if response["type"] == "book":
            symbol = response["symbol"]
            print(symbol, response["buy"][0], response["sell"][0])
            BUYS[symbol] = response["buy"]
            SELLS[symbol] = response["sell"]
            print(symbol, len(BUYS[symbol]), len(SELLS[symbol]))
    # A common mistake people make is to call write_to_exchange() > 1
    # time for every read_from_exchange() response.
    # Since many write messages generate marketdata, this will cause an
    # exponential explosion in pending messages. Please, don't do that!

if __name__ == "__main__":
    main()
