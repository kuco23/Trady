from datetime import datetime, timedelta

from pandas import DataFrame
from sqlalchemy import MetaData, create_engine

from lib import config as cfg
from lib.enums import Trade, Symbol
from lib.graphics import drawHistory
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
        # print(ncandles, len(self._buffer_candles[symbol]))

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

    symbol = Symbol.ADAUSDT
    strategy = meanRevisionTrendWrapper(symbol)

    sd = datetime(2021, 9, 12) # starting time of the strategy backtest
    se = datetime(2021, 10, 11) # ending time of the strategy backtest
    dt = timedelta(minutes=1) # strategy is called after every dt from sd on

    data = Data(sd, se, dt)
    state = {'asset': {'ADA': 0, 'USDT': 100}, 'actions': []}

    history = []

    while data.now < data.end:
        strategy(data, state)
        while state['actions']:
            pos, sym = state['actions'].pop()
            base, quote = sym.name[:3], sym.name[3:]
            price = data.price(sym)
            asset = state['asset']
            if pos == Trade.BUY:
                asset[base] = asset[quote] / price * 0.999
                asset[quote] = 0
                history.append((data.now, Trade.BUY))
                print(base, asset[base])
            elif pos == Trade.SELL:
                asset[quote] = asset[base] * price * 0.999
                asset[base] = 0
                history.append((data.now, Trade.SELL))
                print(quote, asset[quote])
        data.moveTime()

    data.close()
    drawHistory(sd, se, history)
        
