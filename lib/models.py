from abc import ABC
from datetime import datetime, timedelta
from dataclasses import dataclass

from .enums import Symbol, Trade


state_template = {
    'assets': {sym.value[0]: 0 for sym in Symbol},
    'actions': []
}

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

@dataclass
class TradeAction:
    trade: Trade
    symbol: Symbol
    quantity: float = None
    ratio: float = None

@dataclass
class TradeRecord:
    time: datetime
    trade: Trade
    symbol: Symbol
    quantity: float
    price: float