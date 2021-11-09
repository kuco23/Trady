from talib import SMA, EMA

from ...enums import Trade, Symbol
from ...models import TradeAction

class BubbleFind:

    def __init__(self, symbols):
        self.symbols = symbols

    def bubbleFind(self, data, state):
        assets, actions = state['assets'], state['actions']
        
        maxval, maxsym = 0, None
        for symbol in self.symbols:
            base, quote = symbol.value
            ab, aq = assets[base], assets[quote]
            if ab == 0 and aq == 0: continue

            candles1h = data.candles(symbol, 60)
            candles10m = data.candles(symbol, 10)

            sma1h = candles1h.close.sum() / 60
            sma10m = candles10m.close.sum() / 10

            dsma = sma10m / sma1h
            if dsma > maxval and aq > 0:
                maxval = dsma
                maxsym = symbol
            elif dsma < 1 and ab > 0:
                actions.append(TradeAction(
                    Trade.SELL, symbol, ab
                ))

        if maxval > 0:
            base, quote = maxsym.value
            actions.append(TradeAction(
                Trade.BUY, maxsym, assets[quote]
            ))
