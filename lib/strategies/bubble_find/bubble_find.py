from talib import SMA, EMA

from ...enums import Trade, Symbol
from ...models import TradeAction

# trading USDT for multiple coins
def bubbleFindWrapper(symbols):
    
    def bubbleFind(data, state):
        assets = state['assets']
        for symbol in symbols:
            base, quote = symbol.value
            bq, qq = assets[base], assets[quote]
            if bq == 0 and qq == 0: continue

            candles1d = data.candles(symbol, 60 * 24)
            candles1h = data.candles(symbol, 60)
            
            sma1d = SMA(candles1d.close[:30:]).iloc[-1]
            sma1h = SMA(candles1h.close).iloc[-1]
            dsma = sma1h / sma1d

            actions = state['actions']
            if bq > 0 and dsma > 1.01:
                actions.append(TradeAction(
                    Trade.BUY, symbol, assets[quote]
                ))
            elif qq > 0 and dsma < 0.99:
                actions.append(TradeAction(
                    Trade.BUY, symbol, assets[base]
                ))
                
    return bubbleFind
            
bubble_find_export = {
    'wrapper': bubbleFindWrapper,
    'symbols': 'more'
}
