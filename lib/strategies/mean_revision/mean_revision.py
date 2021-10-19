from talib import SMA

from ...enums import Trade
from ...models import Action

def meanRevisionWrapper(symbol):
    base, quote = symbol.value

    def meanRevision(data, state):
        candles1m = data.candles(symbol, 60 * 24 * 30)
        candles1h = data.candles(symbol, 60)
        price = data.price(symbol)

        sma1m = float(SMA(candles1m.close).tail(1))
        sma1h = float(SMA(candles1d.close).tail(1))

        assets = state['assets']
        if sma1h < sma1h * 0.9 and assets[base] > 0:
            state['actions'].append((assets[base], Trade.BUY))
        if sma1h > sma1h * 
        
        
