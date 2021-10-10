from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from sqlalchemy import MetaData, create_engine, desc

from lib import config as cfg
from lib.enums import Trade, Symbol
from lib.strategies import meanRevisionTrendWrapper

# the backtesting relies on the fact that the candles in the database
# are ordered by descendingly by date and spaced exactly 1 minute apart

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
        
        self.sqlengine = create_engine(cfg.SQLALCHEMY_SQLITE, echo=False)
        self.metadata = MetaData(bind=self.sqlengine)
        self.metadata.reflect(self.sqlengine)
        self.conn = self.sqlengine.connect()

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
        self._buffer_candles[symbol] = pd.DataFrame(dict(
            zip(table.columns.keys(), zip(*candles))
        ))
            
    # candle interval is always 1 minute, so calling getCandles with
    # ncandles=n results in n minutes of last candle data
    def getCandles(self, symbol, ncandles):
        if (
            self.now - ncandles * self._minute < self._buffer_start[symbol] or
            self.now > self._buffer_end[symbol]
        ): self._getBufferCandles(symbol, ncandles)
        bi = self._buffer_index[symbol]
        return self._buffer_candles[symbol][bi - ncandles + 1:bi + 1]

    def moveTime(self):
        self.now += self.dt
        for sym in Symbol: self._buffer_index[sym] += self._dm
    

if __name__ == '__main__':

    symbol = Symbol.ADAUSDT
    strategy = meanRevisionTrendWrapper(symbol)

    sd = datetime(2021, 1, 3) # starting time of the strategy backtest
    se = datetime(2021, 1, 29) # ending time of the strategy backtest
    dt = timedelta(minutes=1) # strategy is called after every dt from sd on

    data = Data(sd, se, dt)
    state = {'asset': {'ADA': 0, 'USDT': 100}, 'actions': []}

    while data.now < data.end:
        strategy(data, state)
        while state['actions']:
            pos, sym = state['actions'].pop()
            base, quote = sym.name[:3], sym.name[3:]
            close = float(data.getCandles(sym, 1).close)
            asset = state['asset']
            if pos == Trade.BUY:
                asset[base] = asset[quote] / close * 0.999
                asset[quote] = 0
                print(base, asset[base])
            elif pos == Trade.SELL:
                asset[quote] = asset[base] * close * 0.999
                asset[base] = 0
                print(quote, asset[quote])
        data.moveTime()
        
