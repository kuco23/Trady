from datetime import datetime, timedelta
from time import sleep

from pandas import DataFrame
from binance.client import Client
from binance.enums import *

from lib import config as cfg
from lib.enums import Trade, Symbol, BinanceCandle
from lib.exceptions import OrderFillTimeout, InvalidPosition
from lib.strategies import meanRevisionTrendWrapper

# get_klines(symbol=, interval=)
'''
[
    [
        1499040000000,      # Open time
        "0.01634790",       # Open
        "0.80000000",       # High
        "0.01575800",       # Low
        "0.01577100",       # Close
        "148976.11427815",  # Volume
        1499644799999,      # Close time
        "2434.19055334",    # Quote asset volume
        308,                # Number of trades
        "1756.87402397",    # Taker buy base asset volume
        "28.46694368",      # Taker buy quote asset volume
        "17928899.62484339" # Can be ignored
    ]
]
'''

# get_exchange_info() -> valid symbols ['symbols']
# get_account()
# get_asset_balance(asset, **kwargs)
# get_trade_fee(**kwargs)

# order_market_sell(symbol=, quantity=) -> sell quantity symbol[0] for symbol[1]
# order_market_buy(symbol=, quantity=) -> buy quantity symbol[0] for symbol[1]


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
            base, quote = sym.name[:3], sym.name[3:]
            price = data.price(sym)

            now = datetime.now()
            assets = state['assets']
            order_filled = False
            if pos == Trade.BUY:
                resp = client.order_market_buy(symbol=sym, quantity=quant)
                order_filled = resp['status'] == 'FILLED'
                order_id = resp['id']
                history.append((now, Trade.BUY))
            elif pos == Trade.SELL:
                resp = client.order_market_sell(symbol=sym, quantity=quant)
                order_filled = resp['status'] == 'FILLED'
                order_id = resp['id']
                history.append((now, Trade.SELL))
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
            
