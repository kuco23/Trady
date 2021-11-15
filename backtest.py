from numpy import zeros
from pandas import DataFrame
from sqlalchemy import MetaData, create_engine
from tqdm import tqdm

from lib import config as cfg
from lib.cli import Argparser
from lib.enums import Symbol, Trade
from lib.exceptions import (
    InvalidPosition, DatabaseCandleError, InsufficientData
)
from lib.graphics import drawHistory
from lib.models import AbstractData, TradeRecord

# the backtesting relies on the fact that the candles in the database
# are ordered descendingly by date and spaced exactly 1 minute apart

# Data methods will always return pandas table (to comply with talib)
class Data(AbstractData):
    _bufflen = 10000 # length of the buffer candles

    def __init__(self, sd, se, dt):
        self._dm = dt // self._minute
        self._bfc = {sym: [] for sym in Symbol}
        self._bfs = {sym: sd for sym in Symbol}
        self._bfe = {sym: sd for sym in Symbol}
        self._bfi = {sym: -1 for sym in Symbol}
        
        self.dt = dt
        self.now = sd
        self.end = se
        
        self.db = create_engine(cfg.SQLALCHEMY_SQLITE, echo=False)
        self.metadata = MetaData(bind=self.db)
        self.metadata.reflect(self.db)
        self.conn = self.db.connect()

    def _getTable(self, symbol):
        return self.metadata.tables['candles' + symbol.name]

    def _candlesByDate(self, symbol, sd, ed):
        table = self._getTable(symbol)
        sql_select = table.select().where(
            (sd <= table.c.opentime) & (table.c.opentime < ed)
        ).order_by(table.c.opentime)
        candles = self.conn.execute(sql_select)
        colnames = table.columns.keys()
        return DataFrame(dict(zip(colnames, zip(*candles))))

    def _getBufferCandles(self, symbol, ncandles):
        self._bfi[symbol] = ncandles - 1
        self._bfs[symbol] = self.now - ncandles * self._minute
        self._bfe[symbol] = self.now + self._bufflen * self._minute
        self._bfc[symbol] = self._candlesByDate(
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
        if len(df) != ncandles: raise DatabaseCandleError()
        return df

    def price(self, symbol):
        return float(self.candles(symbol, 1).close)

    def moveTime(self):
        self.now += self.dt
        for sym in Symbol: self._bfi[sym] += self._dm

    def close(self):
        self.conn.close()
        self.db.dispose()
        del self


if __name__ == '__main__':

    fee = 0.001 # binance max fee
    q = 1 - fee

    argparser = Argparser()
    argparser.add_argument_strategy()
    argparser.add_argument_start_date()
    argparser.add_argument_end_date()
    argparser.add_argument_time_interval()
    args = argparser.parse_args()
    
    data = Data(args.sd, args.ed, args.ti)
    state = {
        'assets': {sym.value[0]: 0 for sym in Symbol},
        'actions': []
    }
    state['assets']['USDT'] = 100

    # trades is dynamic, shouldn't be too long anyway
    iterations = (args.ed - args.sd) // args.ti
    history, trades = zeros(iterations), []

    # run historic trade simulation
    with tqdm(total=iterations) as pb:
        
        while data.now < data.end:
            args.strategy(data, state)
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

    print('max value:', history.max())
    print('min value:', history.min())
    print('end value:', history.take(-1))
    print('number of trades:', len(trades))

    drawHistory(data, history, trades, args.sd, args.ed)
    data.close()
