from datetime import datetime, timedelta
from time import sleep

from pandas import DataFrame
from binance.client import Client
from binance.enums import *

from lib import config as cfg
from lib.enums import Trade, Symbol, BinanceCandle
from lib.exceptions import OrderFillTimeout, InvalidPosition
from lib.strategies import meanRevisionTrendWrapper


class Data:
    _minute = timedelta(minutes=1)
    _candleattr = [e.name for e in BinanceCandle]
    
    def __init__(self, client):
        self.client = client

    def candles(self, symbol, ncandles):
        candles = self.client.get_klines(
            symbol=symbol.name,
            interval=KLINE_INTERVAL_1MINUTE,
            limit=ncandles
        )
        return DataFrame(dict(zip(self._candleattr, candles)))

    def price(self, symbol):
        return self.client.get_avg_price(symbol)['price']

def getAssets(client):
    account_data = client.get_account()
    return {
        balance['asset']: balance['free']
        for balance in account_data['balances']
    }

if __name__ == '__main__':

    symbol = Symbol.ADAUSDT
    strategy = meanRevisionTrendWrapper(symbol)
    dt = timedelta(minutes=1)

    client = Client(cfg.BINANCE_API_KEY, cfg.BINANCE_API_SECRET)

    data = Data(client)
    state = {'assets': getAssets(client), 'actions': []}
    history = []

    while True:
        strategy(data, state)
        while state['actions']:
            pos, sym, quant = state['actions'].pop()
            base, quote = sym.value
            price = data.price(sym)

            now = datetime.now()
            assets = state['assets']
            order_filled = False
            if pos == Trade.BUY:
                resp = client.order_market_buy(symbol=sym, quantity=quant)
                order_filled = resp['status'] == 'FILLED'
                order_id = resp['id']
                history.append((now, Trade.BUY, quant, price))
            elif pos == Trade.SELL:
                resp = client.order_market_sell(symbol=sym, quantity=quant)
                order_filled = resp['status'] == 'FILLED'
                order_id = resp['id']
                history.append((now, Trade.SELL, quant, price))
            else: raise InvalidPosition(pos)
               
            slept = 0
            while not order_filled:
                sleep(2)
                slept += 2
                if mt > dt: raise OrderFillTimeout()
                order = client.get_order(symbol=sym, orderId=order_id)
                order_filled = order['status'] == 'FILLED'

            state['assets'] = getAssets(client)
            print(base, state['assets'][base])
            print(quote, state['assets'][quote])
            sleep(dt.seconds - slept)
            
