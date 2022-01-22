from enum import IntEnum
from aenum import Enum, extend_enum

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
    ATOMUSDT = ('ATOM', 'USDT')
    QNTUSDT = ('QNT', 'USDT')
    CLVUSDT = ('CLV', 'USDT')
    AXSUSDT = ('AXS', 'USDT')
    MANAUSDT = ('MANA', 'USDT')
    LINAUSDT = ('LINA', 'USDT')

    def new(name, base, quote):
        return extend_enum(Symbol, name, (base, quote))

class BinanceCandle(Enum):
    OPENTIME = ('opentime', int)
    OPEN = ('open', float)
    HIGH = ('high', float)
    LOW = ('low', float)
    CLOSE = ('close', float)
    VOLUME = ('volume', float)
    CLOSETIME = ('closetime', int)
    QUOTE = ('quote', float)
    TRADES = ('trades', int)
    TAKER_BASE_VOLUME = ('taker_basevol', float)
    TAKER_QUOTE_VOLUME = ('taker_quotevol', float)
    IGNORE = ('ignore', float)
