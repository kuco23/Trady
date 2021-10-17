from enum import Enum, IntEnum

class Trade(IntEnum):
    SELL = 0
    BUY = 1

class Symbol(Enum):
    ADAUSDT = 'ADAUSDT'

class BinanceCandle(Enum):
    OPENTIME = 'opentime'
    OPEN = 'open'
    HIGH = 'high'
    LOW = 'low'
    CLOSE = 'close'
    VOLUME = 'volume'
    CLOSETIME = 'closetime'
    QUOTE = 'quote'
    TRADES = 'trades'
    TAKER_BASE_VOLUME = 'taker_basevol'
    TAKER_QUOTE_VOLUME = 'taker_quotevol'
    IGNORE = 'ignore'
