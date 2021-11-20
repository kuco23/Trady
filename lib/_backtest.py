from copy import deepcopy
from numpy import zeros
from tqdm import tqdm

from . import CandleBrowser
from .enums import Symbol, Trade
from .exceptions import InvalidPosition, DatabaseCandleError
from .models import AbstractData, TradeRecord, state_template

# the backtesting relies on the fact that the candles in the database
# are ordered descendingly by date and spaced exactly 1 minute apart

fee = 0.001 # binance max fee
q = 1 - fee

class BacktestData(AbstractData, CandleBrowser):
    _bufflen = 10000 # length of the buffer candles

    def __init__(self, sd, se, dt):
        super().__init__()

        self._dm = dt // self._minute
        self._bfc = {sym: [] for sym in Symbol}
        self._bfs = {sym: sd for sym in Symbol}
        self._bfe = {sym: sd for sym in Symbol}
        self._bfi = {sym: -1 for sym in Symbol}
        
        self.dt = dt
        self.now = sd
        self.end = se

    def _getBufferCandles(self, symbol, ncandles):
        self._bfi[symbol] = ncandles - 1
        self._bfs[symbol] = self.now - ncandles * self._minute
        self._bfe[symbol] = self.now + self._bufflen * self._minute
        self._bfc[symbol] = self.candlesByDate(
            symbol, self._bfs[symbol], self._bfe[symbol]
        )
            
    # candle interval is always 1 minute, so calling getCandles with
    # ncandles=n results in n minutes of last candle data
    def candles(self, symbol, ncandles):
        if (
            self.now - ncandles * self._minute < self._bfs[symbol] or
            self.now > self._bfe[symbol]
        ): self._getBufferCandles(symbol, ncandles)
        bfi = self._bfi[symbol]
        df = self._bfc[symbol][bfi - ncandles + 1:bfi + 1]
        if len(df) != ncandles: raise DatabaseCandleError(symbol)
        return df

    def moveTime(self):
        self.now += self.dt
        for sym in Symbol: self._bfi[sym] += self._dm

class BacktestEngine:

    def __init__(self, strategy):
        self.strategy = strategy
    
    def backtest(self, sd, ed, ti):
        state = deepcopy(state_template)
        state['assets']['USDT'] = 100

        it = (ed - sd) // ti # number of iterations
        history, trades = zeros(it), []

        # run historic trade simulation
        with BacktestData(sd, ed, ti) as data, tqdm(total=it) as pb:
            
            while data.now < data.end:
                self.strategy(data, state)
                while state['actions']:
                    assets = state['assets']
                    action = state['actions'].pop()
                    action.setQuantityFromRatio(assets)

                    base, quote = action.symbol.value
                    price = data.price(action.symbol)

                    if action.trade == Trade.BUY:
                        assets[base] += action.quantity / price * q
                        assets[quote] -= action.quantity
                    elif action.trade == Trade.SELL:
                        assets[quote] += action.quantity * price * q
                        assets[base] -= action.quantity
                    else: raise InvalidPosition(action.trade)
                    
                    trades.append(TradeRecord(
                        data.now, action.trade, action.symbol,
                        action.quantity, price
                    ))

                # could be calculated externaly from trades
                history[pb.n] = data.portfolioValue(state['assets'])

                data.moveTime()
                pb.update(1)
        
        return history, trades