from numpy import zeros
from sqlalchemy import MetaData, create_engine
from tqdm import tqdm

from . import cfg, CandleBrowser
from .enums import Symbol, Trade
from .exceptions import InvalidPosition, DatabaseCandleError
from .graphics import drawHistory
from .models import AbstractData, TradeRecord, state_template

# the backtesting relies on the fact that the candles in the database
# are ordered descendingly by date and spaced exactly 1 minute apart

fee = 0.001 # binance max fee
q = 1 - fee

# Data methods will always return pandas table (to comply with talib)
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

    def price(self, symbol):
        return float(self.candles(symbol, 1).close)

    def moveTime(self):
        self.now += self.dt
        for sym in Symbol: self._bfi[sym] += self._dm

class BacktestEngine:

    def __init__(self, strategy):
        self.strategy = strategy
    
    def backtest(self, sd, ed, ti):
        data = BacktestData(sd, ed, ti)
        state = state_template
        state['assets']['USDT'] = 100

        # trades is dynamic, shouldn't be too long anyway
        iterations = (sd - ed) // ti
        history, trades = zeros(iterations), []

        # run historic trade simulation
        with tqdm(total=iterations) as pb:
            
            while data.now < data.end:
                self.strategy(data, state)
                while state['actions']:
                    action = state['actions'].pop()
                    assets = state['assets']
                    base, quote = action.symbol.value
                    price = data.price(action.symbol)
                    
                    if action.quantity is not None:
                        quantity = action.quantity
                    elif action.trade == Trade.BUY:
                        quantity = assets[quote] * action.ratio
                    elif action.trade == Trade.SELL:
                        quantity = assets[base] * action.ratio
                    
                    if action.trade == Trade.BUY:
                        assets[base] += quantity / price * q
                        assets[quote] -= quantity
                    elif action.trade == Trade.SELL:
                        assets[quote] += quantity * price * q
                        assets[base] -= quantity
                    else: raise InvalidPosition(action.trade)
                    
                    trades.append(TradeRecord(
                        data.now, action.trade, action.symbol,
                        quantity, price
                    ))

                # should be calculated externaly from trades
                history[pb.n] = data.portfolioValue(state['assets'])

                data.moveTime()
                pb.update(1)

        data.close()
        
        return history, trades