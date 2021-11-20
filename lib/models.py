from abc import ABC
from datetime import datetime, timedelta
from dataclasses import dataclass

from .enums import Symbol, Trade


# N.B. that TradeAction.quantity is supposed to be
# the amount of TradeAction.symbol.value[1] sold
# to buy TradeAction.symbol.value[0] in the
# case of TradeAction.trade == Trade.BUY (and vice-versa)

state_template = {
    'assets': {sym.value[0]: 0 for sym in Symbol},
    'actions': []
}

class AbstractData(ABC):
    _minute = timedelta(minutes=1)

    def candles(self, symbol, ncandles):
        raise NotImplementedError()

    def price(self, symbol):
        return self.candles(symbol, 1).close.iloc[-1]

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
    iquantity: float = None
    _price: float = None

    @property
    def price(self): return self._price

    @price.setter
    def price(self, value):
        self._setInvertedQuantity(value)

    # this is really what you want when setting the price
    def _setInvertedQuantity(self, symbol_price):
        match self.trade:
            case Trade.BUY: 
                self.iquantity = self.quantity / symbol_price
            case Trade.SELL: 
                self.iquantity = self.quantity * symbol_price

    # set quantity from ratio, if ratio is defined
    def setQuantityFromRatio(self, assets):
        if self.ratio is None: return
        base, quote = self.symbol.value
        match self.trade:
            case Trade.BUY: 
                self.quantity = assets[quote] * self.ratio
            case Trade.SELL:
                self.quantity = assets[base] * self.ratio

@dataclass
class TradeRecord:
    time: datetime
    trade: Trade
    symbol: Symbol
    quantity: float
    price: float