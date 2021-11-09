import numpy as np
from talib import RSI, EMA

from ...enums import Trade, Symbol
from ...models import TradeAction

class MeanRevisionTrend:

    def __init__(self, symbols):
        self.symbol = symbols[0]
        self.b, self.q = self.symbol.value
    
    def meanRevisionTrend(self, data, state):
        candles1d = data.candles(self.symbol, 24 * 60).iloc[::30,:]
        candles1h = data.candles(self.symbol, 60)
        
        ema1d = EMA(candles1d.close).iloc[-1]
        ema1h = EMA(candles1h.close).iloc[-1]
        rsi = RSI(candles1h.close).iloc[-1]

        assets = state['assets']
        if ema1h > ema1d and rsi < 30 and assets[self.q] > 0:
            state['actions'].append(TradeAction(
                Trade.BUY, symbol, assets[self.q]
            ))
        elif ema1h < ema1d and rsi > 70 and assets[self.b] > 0:
            state['actions'].append(TradeAction(
                Trade.SELL, symbol, assets[self.b]
            ))
