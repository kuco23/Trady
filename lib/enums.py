from enum import Enum, IntEnum

class Trade(IntEnum):
    SELL = 0
    BUY = 1

class Symbol(Enum):
    ADAUSDT = 'ADAUSDT'

class CandleColumn(Enum):
    pass
