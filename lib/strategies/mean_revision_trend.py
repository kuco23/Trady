from talib import RSI, EMA

def meanRevisionTrend(prices_1day, prices_1h, state):
    ema_1h = EMA(prices_1h)
    ema_1day = EMA(prices_1day)

    if (
        ema_1h[-1] > ema_1day[-1] and
        rsi[-1] < 40 and
        not state.has_position
    ): return 'buy'

    if (
        ema_1h[-1] < ema_1day[-1] and
        rsi[-1] > 60 and
        state.has_position
    ): return 'sell'
