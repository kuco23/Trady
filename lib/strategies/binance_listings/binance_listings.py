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
        n = len(diff)

        actions = state['actions']
        for symbol_name in diff: 
            if symbol_name in Symbol:
                symbol = Symbol.__getitem__(symbol_name)
                base, quote = symbol.value
            else:
                base, quote = data.symbolBaseQuote(symbol_name)
                symbol = Symbol.new(symbol_name, base, quote)
            actions.append(TradeAction(Trade.BUY, symbol, ratio=1/n))
        
        print(n)
    
    return binanceListings

