from talib import EMA, RSI

from ...enums import Trade
from ...models import TradeAction

def trendSpreadWrapper(symbols):
    treshold = round(0.75 * len(symbols))

    def trendSpread(data, state):
        assets = state['assets']
        actions = state['actions']

        bulls, bears = [], []
        for symbol in symbols:
            base, quote = symbol.value
            if assets[base] == 0 and assets[quote] == 0: 
                continue

            candles1d = data.candles(symbol, 60 * 24)

            ema1d = EMA(candles1d.close.iloc[::30], 40).iloc[0]
            ema1h = EMA(candles1d.close, 40).iloc[-1]
            rsi = RSI(candles1d.close).iloc[-1]

            if ema1h > ema1d and rsi < 25:
                bulls.append(symbol)
            elif ema1h < ema1d and rsi > 65:
                bears.append(symbol)

        for symbol in bears:
            base, quote = symbol.value
            if assets[base] == 0: continue
            actions.append(TradeAction(
                Trade.SELL, symbol, ratio=1
            ))                  

        if len(bulls) >= treshold:
            for symbol in bulls:
                base, quote = symbol.value
                if assets[quote] == 0: continue
                actions.append(TradeAction(
                    Trade.BUY, symbol, ratio=1/len(bulls)
                ))
    
    return trendSpread
