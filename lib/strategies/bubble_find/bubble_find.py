from talib import SMA, EMA

from ...enums import Trade, Symbol
from ...models import TradeAction

# trading USDT for multiple coins
def bubbleFindWrapper(symbols):
    symbols = list(Symbol.__members__.values())
    
    def bubbleFind(data, state):
        assets = state['assets']
        for symbol in symbols:
            base, quote = symbol.value
            bq, qq = assets[base], assets[quote]
            if bq == 0 and qq == 0: continue
            
            candles = data.candles(symbol, 30)
            sma = EMA(candles.close).iloc[-1]
            diffsma = SMA(candles.close.diff()).iloc[-1]

            actions = state['actions']
            if bq > 0 and diffsma > 0.001 * sma:
                actions.append(TradeAction(
                    Trade.BUY, symbol, assets[quote]
                ))
            elif qq > 0 and diffsma < -0.001 * sma:
                actions.append(TradeAction(
                    Trade.BUY, symbol, assets[base]
                ))
                
    return bubbleFind
            
            
