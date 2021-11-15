from abc import ABC
from datetime import timedelta
from collections import namedtuple

from .enums import Symbol

class AbstractData(ABC):
    _minute = timedelta(minutes=1)

    def candles(self, symbol, ncandles):
        raise NotImplementedError()

    def price(self, symbol):
        raise NotImplementedError()

    # in USDT
    def portfolioValue(self, assets):
        value = assets['USDT']
        for coin, amount in assets.items():
            if amount == 0 or coin == 'USDT': continue
            sym = Symbol.__members__.get(coin + 'USDT')
            value += amount * self.price(sym)
        return value

TradeAction = namedtuple(
    'action', ('trade', 'symbol', 'quantity', 'ratio'),
    defaults = (None, None, None, None)
)
TradeRecord = namedtuple(
    'history_record', ('time', 'trade', 'symbol', 'quantity', 'price')
)
