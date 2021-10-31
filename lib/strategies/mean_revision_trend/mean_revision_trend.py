import numpy as np
from talib import RSI, EMA

from ...enums import Trade, Symbol
from ...models import TradeAction

def meanRevisionTrendWrapper(symbol):
    base, quote = symbol.value
    
    def meanRevisionTrend(data, state):
        candles1d = data.candles(symbol, 24 * 60).iloc[::30,:]
        candles1h = data.candles(symbol, 60)
        
        ema1d = EMA(candles1d.close).iloc[-1]
        ema1h = EMA(candles1h.close).iloc[-1]
        rsi = RSI(candles1h.close).iloc[-1]

        assets = state['assets']
        if ema1h > ema1d and rsi < 30 and assets[quote] > 0:
            state['actions'].append(TradeAction(
                Trade.BUY, symbol, assets[quote]
            ))
        elif ema1h < ema1d and rsi > 70 and assets[base] > 0:
            state['actions'].append(TradeAction(
                Trade.SELL, symbol, assets[base]
            ))

    return meanRevisionTrend

mean_revision_trend_export = {
    'wrapper': meanRevisionTrendWrapper,
    'symbols': 'any'
}
