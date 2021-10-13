from datetime import datetime, timedelta
from time import sleep

from pandas import DataFrame
from sqlalchemy import MetaData, create_engine
from binance import Client
from binance.enums import *

from lib import config as cfg
from lib.enums import Trade, Symbol
#from lib.graphics import drawHistory
from lib.strategies import meanRevisionTrendWrapper

class Data:
    _minute = timedelta(minutes=1)

    candleattr = [
        'opentime', 'open', 'high', 'low', 'close',
        'volume', 'closetime', 'quote', 'trades',
        'taker_basevol', 'taker_quotevol', 'ignore'
    ]
    
    def __init__(self, client):
        self.client = client

    def candles(self, symbol, ncandles):
        candles = self.client.get_klines(
            symbol=symbol.name,
            interval=KLINE_INTERVAL_1MINUTE,
            limit=ncandles
        )
        return DataFrame(dict(zip(self.candleattr, zip(*candles))))

    def price(self, symbol):
        return self.client.get_avg_price(symbol)['price']
            

if __name__ == '__main__':

    symbol = Symbol.ADAUSDT
    strategy = meanRevisionTrendWrapper(symbol)

    dt = timedelta(minutes=1)

    client = Client(cfg.BINANCE_API_KEY, cfg.BINANCE_API_SECRET)

    data = Data(client)
    state = {'asset': {'USDT': 100, 'ADA': 0}, 'actions': []}

    history = []

    while True:
        now = datetime.now()
        strategy(data, state)
        while state['actions']:
            pos, sym = state['actions'].pop()
            base, quote = sym.name[:3], sym.name[3:]
            price = data.price(sym)
            asset = state['asset']
            if pos == Trade.BUY:
                asset[base] = asset[quote] / price * 0.999
                asset[quote] = 0
                history.append((now, Trade.BUY))
                print(base, asset[base])
            elif pos == Trade.SELL:
                asset[quote] = asset[base] * price * 0.999
                asset[base] = 0
                history.append((now, Trade.SELL))
                print(quote, asset[quote])

        sleep(dt.seconds)
