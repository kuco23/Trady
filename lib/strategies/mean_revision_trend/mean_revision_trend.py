import numpy as np
from talib import RSI, EMA
from ...enums import Trade, Symbol


def meanRevisionTrendWrapper(symbol):
    base, quote = symbol.name[:3], symbol.name[3:]
    
    def meanRevisionTrend(data, state):
        candles1h = data.getCandles(symbol, 60)
        candles1d = data.getCandles(symbol, 24 * 60)
        
        ema1h = float(EMA(candles1h.open).tail(1))
        ema1d = float(EMA(candles1d.open).tail(1))
        rsi = float(RSI(candles1h.open).tail(1))

        if ema1h > ema1d and rsi < 40 and state['asset'][quote] > 0:
            state['actions'].append((Trade.BUY, symbol))
        elif ema1h < ema1d and rsi > 60 and state['asset'][base] > 0:
            state['actions'].append((Trade.SELL, symbol))

    return meanRevisionTrend
