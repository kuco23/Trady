import numpy as np
from talib import RSI, EMA
from ...enums import Trade, Symbol


def meanRevisionTrendWrapper(symbol):
    base, quote = symbol.value
    
    def meanRevisionTrend(data, state):
        candles1h = data.candles(symbol, 60)
        candles1d = data.candles(symbol, 24 * 60)
        
        ema1h = float(EMA(candles1h.close).tail(1))
        ema1d = float(EMA(candles1d.close).tail(1))
        rsi = float(RSI(candles1h.close).tail(1))

        if ema1h > ema1d and rsi < 30 and state['assets'][quote] > 0:
            state['actions'].append(
                (Trade.BUY, symbol, state['assets'][quote])
            )
        elif ema1h < ema1d and rsi > 70 and state['assets'][base] > 0:
            state['actions'].append(
                (Trade.SELL, symbol, state['assets'][base])
            )

    return meanRevisionTrend
