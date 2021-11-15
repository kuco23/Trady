from enum import Enum, IntEnum

class Trade(IntEnum):
    SELL = 0
    BUY = 1

class Symbol(Enum):
    BTCUSDT = ('BTC', 'USDT')
    BCHUSDT = ('BCH', 'USDT')
    BTTUSDT = ('BTT', 'USDT')
    ADAUSDT = ('ADA', 'USDT')
    DOTUSDT = ('DOT', 'USDT')
    DOGEUSDT = ('DOGE', 'USDT')
    SHIBUSDT = ('SHIB', 'USDT')
    ICPUSDT = ('ICP', 'USDT')
    CVCUSDT = ('CVC', 'USDT')
    BNBUSDT = ('BNB', 'USDT')
    SOLUSDT = ('SOL', 'USDT')
    POLYUSDT = ('POLY', 'USDT')
    TRXUSDT = ('TRX', 'USDT')
    XTZUSDT = ('XTZ', 'USDT')
    SUSHIUSDT = ('SUSHI', 'USDT')
    CAKEUSDT = ('CAKE', 'USDT')
    XRPUSDT = ('XRP', 'USDT')
    CRVUSDT = ('CRV', 'USDT')
    LUNAUSDT = ('LUNA', 'USDT')

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
