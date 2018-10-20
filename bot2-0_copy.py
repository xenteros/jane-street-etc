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
test_mode = False

# This setting changes which test exchange is connected to.
# 0 is prod-like
# 1 is slower
# 2 is empty
test_exchange_index=0
prod_exchange_hostname="production"
LAST_ORDER_ID = int(time.time())

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

def buy(exchange, price, size, symbol):
    obj = {"type": "add", "order_id": getId(), "symbol": symbol, "dir": "BUY", "price": price, "size": size}
    json.dump(obj, exchange)
    exchange.write("\n")

def convert(operation = "BUY", exchange, size, symbol, operation):
    obj = {"type": "convert", "order_id": getId(), "symbol": symbol, "dir": operation, "size": size}
    json.dump(obj, exchange)
    exchange.write("\n")

def sell(exchange, price, size, symbol):
    obj = {"type": "add", "order_id": getId(), "symbol": symbol, "dir": "SELL", "price": price, "size": size}
    json.dump(obj, exchange)
    exchange.write("\n")

def arbitrage_ADR(exchange):
    VALE_buy = get_price(symbol = "VALE", operation = 'buy')
    VALE_sell = get_price(symbol = "VALE", operation = 'sell')
    VALBZ_buy = get_price(symbol = 'VALBZ', operation = 'buy')
    VALBZ_sell = get_price(symbol = 'VALBZ', operation = 'sell')

    print(VALBZ_sell)
    
    if VALBZ_buy == -1 or VALE_sell == -1:
        pass
    elif VALBZ_buy > VALE_sell + 10:
        # Buy VALE
        buy(exchange, VALE_sell, 1, "VALE")
        # Convert to VALBZ
        convert(exchange, 1, "VALBZ", "BUY")
        # Sell VALBZ
        sell(exchange, VALBZ_buy, 1, "VALBZ")
        
    if VALBZ_sell == -1 or VALE_buy == -1:
        pass
    elif VALBZ_sell + 10 < VALE_buy:
        # Buy VALBZ
        buy(exchange, VALBZ_sell, 1, "VALBZ")
        # Convert to VALE
        convert(exchange, 1, "VALE", "BUY")
        # Sell VALE
        sell(exchange, VALE_buy, 1, "VALE")
        
def arbitrage_XLF(exchange):
    XLF_buy = get_price(symbol = "XLF", operation = 'buy')[0][0]
    XLF_sell = get_price(symbol = "XLF", operation = 'sell')[0][0]
    BOND_buy = get_price(symbol = "BOND", operation = 'buy')[0][0]
    BOND_sell = get_price(symbol = "BOND", operation = 'sell')[0][0]
    GS_buy = get_price(symbol = "GS", operation = 'buy')[0][0]
    GS_sell = get_price(symbol = "GS", operation = 'sell')[0][0]
    MS_buy = get_price(symbol = "MS", operation = 'buy')[0][0]
    MS_sell = get_price(symbol = "MS", operation = 'sell')[0][0]
    WFC_buy = get_price(symbol = "WFC", operation = 'buy')[0][0]
    WFC_sell = get_price(symbol = "WFC", operation = 'sell')[0][0]
    
    if XLF_buy == -1 or BOND_sell == -1 or GS_sell == -1 or MS_sell == -1 or WFC_sell == -1:
        pass
    elif XLF_buy > 3/10*BOND_sell + 2/10*GS_sell + 3/10*MS_sell+ 2/10*WFC_sell + 10:
        buy(exchange, BOND_sell, 3, "BOND")
        buy(exchange, BOND_sell, 2, "GS")
        buy(exchange, BOND_sell, 3, "MS")
        buy(exchange, BOND_sell, 2, "WFC")
        convert(exchange, 10, "XLF", "BUY")
        sell(exchange, XLF_buy, 10, "XLF")
    
    if XLF_sell == -1 or BOND_buy == -1 or GS_buy == -1 or MS_buy == -1 or WFC_buy == -1:
        pass
    elif XLF_sell + 10 < 3/10*BOND_buy + 2/10*GS_buy + 3/10*MS_buy+ 2/10*WFC_buy + 10:
        buy(exchange, XLF_sell, 10, "XLF")
        convert(exchange, 10, "XLF", "SELL")
        sell(exchange, BOND_sell, 3, "BOND")
        sell(exchange, BOND_sell, 2, "GS")
        sell(exchange, BOND_sell, 3, "MS")
        sell(exchange, BOND_sell, 2, "WFC")

        
        
        
    
    
    

    
                    
    
    

def get_price(symbol, operation):
    if operation == "buy":
        return BUYS[symbol][0][0] if BUYS[symbol] else -1
    if operation == "sell":
        return SELLS[symbol][0][0] if SELLS[symbol] else -1
    return -1
# ~~~~~============== helpers ==============~~~~~

def getId():
    t = time.time()
    if t - LAST_ORDER_ID < 1.5:
        time.sleep(1)
    return int(time.time())

# ~~~~~============== MAIN LOOP ==============~~~~~

def main():
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    hello_from_exchange = read_from_exchange(exchange)
    
    buy(exchange, 999, 50, "BOND")
    sell(exchange, 1001, 50, "BOND")
    # Initialize portfolio
    print(hello_from_exchange)
    for symbol in hello_from_exchange["symbols"]:
        #print(symbol)
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
        elif response["type"] == "fill":
            pass
        arbitrage_ADR(exchange)
            
        #time.sleep(1)
			
    # A common mistake people make is to call write_to_exchange() > 1
    # time for every read_from_exchange() response.
    # Since many write messages generate marketdata, this will cause an
    # exponential explosion in pending messages. Please, don't do that!

if __name__ == "__main__":
    main()
