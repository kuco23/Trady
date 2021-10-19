from abc import ABC
from datetime import timedelta
from collections import namedtuple

class AbstractData(ABC):
    _minute = timedelta(minutes=1)

    def candles(self, symbol, ncandles):
        raise NotImplementedError()

    def price(self, symbol):
        raise NotImplementedError()

Record = namedtuple('history_record',
    ('time', 'trade', 'symbol', 'quantity', 'price')
)

Action = namedtuple('action', ('trade', 'symbol', 'quantity'))
