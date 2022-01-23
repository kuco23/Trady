# does not support backtesting

from ...enums import Trade, Symbol
from ...models import TradeAction

binance_symbols = set()

def binanceListingsWrapper(*args):

    def binanceListings(data, state):
        global binance_symbols

        # init
        if len(binance_symbols) == 0:
            symbols = data.tradingSymbols()
            binance_symbols = set(symbols)
            return
        
        current_symbols = data.tradingSymbols()
        diff = binance_symbols - set(current_symbols)
        usdts = [d for d in diff if d.endswith('USDT')]

        actions = state['actions']
        for sname in usdts: 
            symbol = (
                Symbol.__getitem__(sname) if sname in Symbol 
                else Symbol.new(sname, sname[:-4], 'USDT')
            )
            actions.append(TradeAction(
                Trade.BUY, symbol, ratio=1/len(usdts)
            ))
            print(sname)
    
    return binanceListings

