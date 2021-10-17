from argparse import ArgumentParser
from datetime import datetime, timedelta

from pandas import DataFrame
from sqlalchemy import MetaData, create_engine

from lib import config as cfg
from lib.enums import Trade, Symbol
from lib.graphics import drawHistory
from lib.strategies import *

# the backtesting relies on the fact that the candles in the database
# are ordered descendingly by date and spaced exactly 1 minute apart

# Data methods will always return pandas table (to comply with talib)
class Data:
    _minute = timedelta(minutes=1)
    _bufflen = 10000 # length of the buffer candles

    def __init__(self, sd, se, dt):
        self._buffer_candles = {sym: [] for sym in Symbol}
        self._buffer_start = {sym: sd for sym in Symbol}
        self._buffer_end = {sym: sd for sym in Symbol}
        self._buffer_index = {sym: -1 for sym in Symbol}
        self._dm = dt // self._minute
        
        self.dt = dt
        self.now = sd
        self.end = se
        
        self.db = create_engine(cfg.SQLALCHEMY_SQLITE, echo=False)
        self.metadata = MetaData(bind=self.db)
        self.metadata.reflect(self.db)
        self.conn = self.db.connect()

    def _getTable(self, symbol):
        return self.metadata.tables['candles' + symbol.name]

    def _getBufferCandles(self, symbol, ncandles):
        self._buffer_index[symbol] = ncandles - 1
        self._buffer_start[symbol] = self.now - ncandles * self._minute
        self._buffer_end[symbol] = self.now + self._bufflen * self._minute
        table = self._getTable(symbol)
        sql_select = table.select().where(
            (self._buffer_start[symbol] < table.c.opentime) &
            (table.c.opentime <= self._buffer_end[symbol])
        )
        candles = self.conn.execute(sql_select)
        self._buffer_candles[symbol] = DataFrame(
            dict(zip(table.columns.keys(), zip(*candles)))
        )

    def moveTime(self):
        self.now += self.dt
        for sym in Symbol: self._buffer_index[sym] += self._dm
            
    # candle interval is always 1 minute, so calling getCandles with
    # ncandles=n results in n minutes of last candle data
    def candles(self, symbol, ncandles):
        if (
            self.now - ncandles * self._minute < self._buffer_start[symbol] or
            self.now > self._buffer_end[symbol]
        ): self._getBufferCandles(symbol, ncandles)
        bi = self._buffer_index[symbol]
        return self._buffer_candles[symbol][bi - ncandles + 1:bi + 1]

    def price(self, symbol):
        return float(self.candles(symbol, 1).close)

    def close(self):
        self.conn.close()
        self.db.dispose()
        del self
    

if __name__ == '__main__':

    argparser = ArgumentParser()
    argparser.add_argument('strategy', type=str, metavar='strategy')
    argparser.add_argument(
        '-sym', type=str, metavar='symbol',
        choices=[sym.name for sym in Symbol]
    )
    argparser.add_argument('-sd', type=str, metavar='start date')
    argparser.add_argument('-ed', type=str, metavar='end date')
    argparser.add_argument(
        '-si', type=int, default=1,
        metavar='strategy time interval in minutes'
    )
    args = argparser.parse_args()

    symbol = None
    for sym in Symbol:
        if sym.name == args.sym: symbol = sym
    strategy = eval(args.strategy + 'Wrapper')(symbol)

    sd = datetime(*map(int, args.sd.split()))
    se = datetime(*map(int, args.ed.split()))
    dt = timedelta(minutes=args.si)
                  
    data = Data(sd, se, dt)
    state = {'assets': {'ADA': 0, 'USDT': 100}, 'actions': []}
    history = []

    while data.now < data.end:
        strategy(data, state)
        while state['actions']:
            pos, sym, quant = state['actions'].pop()
            base, quote = sym.name[:3], sym.name[3:]
            price = data.price(sym)
            assets = state['assets']
            if pos == Trade.BUY:
                assets[base] = quant / price * 0.999
                assets[quote] -= quant
                history.append((data.now, Trade.BUY, quant))
            elif pos == Trade.SELL:
                assets[quote] = quant * price * 0.999
                assets[base] -= quant
                history.append((data.now, Trade.SELL, quant))
            print(base, assets[base])
            print(quote, assets[quote])
        data.moveTime()

    data.close()
    drawHistory(sd, se, history)
        
