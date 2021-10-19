import numpy as np
from talib import RSI, EMA

from ...enums import Trade, Symbol
from ...models import Action

def meanRevisionTrendWrapper(symbol):
    base, quote = symbol.value
    
    def meanRevisionTrend(data, state):
        candles1d = data.candles(symbol, 24 * 60).iloc[::30,:]
        candles1h = data.candles(symbol, 60)
        
        ema1d = float(EMA(candles1d.close).tail(1))
        ema1h = float(EMA(candles1h.close).tail(1))
        rsi = float(RSI(candles1h.close).tail(1))

        assets = state['assets']
        if ema1h > ema1d and rsi < 30 and assets[quote] > 0:
            state['actions'].append(Action(
                Trade.BUY, symbol, assets[quote]
            ))
        elif ema1h < ema1d and rsi > 70 and assets[base] > 0:
            state['actions'].append(Action(
                Trade.SELL, symbol, assets[base]
            ))

    return meanRevisionTrend
