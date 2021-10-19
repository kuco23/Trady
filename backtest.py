from argparse import ArgumentParser
from datetime import datetime, timedelta

from pandas import DataFrame
from sqlalchemy import MetaData, create_engine

from lib import config as cfg
from lib.enums import Trade, Symbol
from lib.models import AbstractData, Record
from lib.graphics import drawHistory
from lib.exceptions import InvalidPosition
from lib.strategies import *

# the backtesting relies on the fact that the candles in the database
# are ordered descendingly by date and spaced exactly 1 minute apart

# Data methods will always return pandas table (to comply with talib)
class Data(AbstractData):
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

    def _candlesByDate(self, symbol, sd, ed):
        table = self._getTable(symbol)
        sql_select = table.select().where(
            (sd < table.c.opentime) & (table.c.opentime <= se)
        )
        candles = self.conn.execute(sql_select)
        colnames = table.columns.keys()
        return DataFrame(dict(zip(colnames, zip(*candles))))

    def _getBufferCandles(self, symbol, ncandles):
        self._buffer_index[symbol] = ncandles - 1
        self._buffer_start[symbol] = self.now - ncandles * self._minute
        self._buffer_end[symbol] = self.now + self._bufflen * self._minute
        self._buffer_candles[symbol] = self._candlesByDate(
            symbol, self._buffer_start[symbol], self._buffer_end[symbol]
        )
            
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

    def moveTime(self):
        self.now += self.dt
        for sym in Symbol: self._buffer_index[sym] += self._dm

    def close(self):
        self.conn.close()
        self.db.dispose()
        del self
    

if __name__ == '__main__':

    fee = 0.001 # binance max fee
    
    argparser = ArgumentParser()
    argparser.add_argument('strategy', metavar='strategy')
    argparser.add_argument('-sym', metavar='symbol',
        choices=list(Symbol.__members__.keys()))
    argparser.add_argument('-sd', metavar='start date')
    argparser.add_argument('-ed', metavar='end date')
    argparser.add_argument('-si', type=int, default=1,
        metavar='strategy time interval in minutes')
    args = argparser.parse_args()

    symbol = Symbol.__members__.get(args.sym)
    strategy = eval(args.strategy + 'Wrapper')(symbol)
    
    sd = datetime(*map(int, args.sd.split()))
    se = datetime(*map(int, args.ed.split()))
    dt = timedelta(minutes=args.si)
                  
    data = Data(sd, se, dt)
    state = {
        'assets': {'USDT': 100, **{sym.value[0]: 0 for sym in Symbol}},
        'actions': []
    }
    history = []

    while data.now < data.end:
        strategy(data, state)
        while state['actions']:
            action = state['actions'].pop()
            base, quote = action.symbol.value
            price = data.price(action.symbol)
            
            assets = state['assets']
            if action.trade == Trade.BUY:
                assets[base] = action.quantity / price * (1 - fee)
                assets[quote] -= action.quantity
            elif action.trade == Trade.SELL:
                assets[quote] = action.quantity * price * (1 - fee)
                assets[base] -= action.quantity
            else: raise InvalidPosition(action.trade)
            
            history.append(Record(
                data.now, action.trade, action.symbol,
                action.quantity, price
            ))
            print(base, assets[base])
            print(quote, assets[quote])
            
        data.moveTime()

    drawHistory(data, history, sd, se)
    data.close()
        
