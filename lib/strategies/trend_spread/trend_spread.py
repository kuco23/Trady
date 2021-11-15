from talib import SMA, EMA, RSI

from ...enums import Trade, Symbol
from ...models import TradeAction

class TrendSpread:

    def __init__(self, symbols):
        self.symbols = symbols
        self.n = len(symbols)
        self.treshold = self.n // 3

    def trendSpread(self, data, state):
        bulls, bears = [], []
        for symbol in self.symbols:

            candles1d = data.candles(symbol, 60 * 24)
            candles1h = data.candles(symbol, 60)

            ema1d = EMA(candles1d.close.iloc[::30], 40).iloc[-1]
            ema1h = EMA(candles1h.close, 40).iloc[-1]
            rsi = RSI(candles1d.close).iloc[-1]

            if ema1h > ema1d and rsi < 25:
                bulls.append(symbol)
            elif ema1h < ema1d and rsi > 65:
                bears.append(symbol)

        for symbol in bears:
            base, quote = symbol.value
            if state['assets'][base] == 0: continue
            state['actions'].append(TradeAction(
                Trade.SELL, symbol, ratio=1
            ))                  

        if len(bulls) >= self.treshold:
            for symbol in bulls:
                base, quote = symbol.value
                state['actions'].append(TradeAction(
                    Trade.BUY, symbol, ratio=1/len(bulls)
                ))