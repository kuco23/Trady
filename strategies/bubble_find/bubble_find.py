from talib import SMA

from ...lib.enums import Trade
from ...lib.models import TradeAction

def bubbleFindWrapper(symbols):

    def bubbleFind(self, data, state):
        assets, actions = state['assets'], state['actions']
        
        maxval, maxsym = 0, None
        for symbol in self.symbols:
            base, quote = symbol.value
            ab, aq = assets[base], assets[quote]
            if ab == 0 and aq == 0: continue

            candles30m = data.candles(symbol, 30)
            candles10m = data.candles(symbol, 10)

            sma30m = SMA(candles30m.close, 30).iloc[-1]
            sma10m = SMA(candles10m.close, 10).iloc[-1]

            dsma = sma10m / sma30m
            if dsma > 1.2 and dsma > maxval and aq > 0:
                maxval = dsma
                maxsym = symbol
            elif dsma < 0.8 and ab > 0:
                actions.append(TradeAction(
                    Trade.SELL, symbol, ab
                ))

        if maxval > 0:
            base, quote = maxsym.value
            actions.append(TradeAction(
                Trade.BUY, maxsym, assets[quote]
            ))
    
    return bubbleFind
