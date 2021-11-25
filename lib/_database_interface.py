from pytz import UTC
from datetime import datetime, timedelta
from json import dump, load
from pathlib import Path

import intervals as I
from pandas import DataFrame
from binance import Client
from binance.enums import KLINE_INTERVAL_1MINUTE
from sqlalchemy import (Column, DateTime, Float, Integer, MetaData, Table,
                        UniqueConstraint, create_engine)
from tqdm import tqdm

from . import cfg
from .enums import Symbol


datapath = Path('data')
datapath.mkdir(exist_ok=True)
minute = timedelta(minutes=1)

class CandleInfoManager: 

    def __init__(self):
        self.path = datapath / cfg.DATABASE_INFOJSON
        self.path.touch()
        self._load()
        self._fillSymbolInfo()

    def _infoTemplate(self, symbol):
        return {'sd': [], 'ed': [], 'loading': False}

    def _fillSymbolInfo(self):
        for symbol in Symbol:
            if symbol.name in self._info: continue
            self._info[symbol.name] = self._infoTemplate(symbol)

    def _load(self):
        if self.path.is_file():
            with open(self.path, 'r') as file:
                self._info = load(file)
        else: self._info = dict()

    def _save(self):
        with open(self.path, 'w') as file:
            dump(self._info, file)

    def _loadIntervals(self, symbol):
        intervals = I.empty()
        syminfo = self._info[symbol.name]
        for sd, ed in zip(syminfo['sd'], syminfo['ed']):
            sdi, edi = map(datetime.fromtimestamp, [sd, ed])
            intervals |= I.closedopen(sdi, edi)
        return intervals

    def _saveIntervals(self, symbol, intervals):
        syminfo = self._info[symbol.name]
        sd, ed = syminfo['sd'], syminfo['ed']
        sd.clear()
        ed.clear()
        for interval in intervals:
            sd.append(interval.lower.timestamp())
            ed.append(interval.upper.timestamp())
        self._save()
    
    def repr(self, symbol):
        intervals = self._loadIntervals(symbol)
        return symbol.name + ' -> ' + ' | '.join([
            f'[{interval.lower}, {interval.upper})'
            for interval in intervals
        ])

    def clearData(self, symbol):
        self._info[symbol.name] = self._infoTemplate(symbol)
        self._save()

    # to figure out which parts are missing when wanting
    # to get [sd, ed) interval of new candle data
    def missingData(self, symbol, sd, ed):
        interval = I.closedopen(sd, ed)
        intervals = self._loadIntervals(symbol)
        return interval - intervals

    # adding interval [sd, ed) of new candle data to info.json
    def dataAdded(self, symbol, sd, ed):
        interval = I.closedopen(sd, ed)
        intervals = self._loadIntervals(symbol)
        self._saveIntervals(symbol, interval | intervals)

    # checking if the interval is included in the database
    def hasData(self, symbol, sd, ed):
        interval = I.closedopen(sd, ed)
        intervals = self._loadIntervals(symbol)
        return intervals.contains(interval)

    def setLoading(self, symbol, is_loading):
        self._info[symbol.name]['loading'] = is_loading
        self._save()

    def loadingCompleted(self, symbol):
        return not self._info[symbol.name]['loading']

class CandleSeeder:

    def __init__(self):
        self.info = CandleInfoManager()
        self.engine = create_engine(cfg.DATABASE_SQLALCHEMY)
        self.metadata = MetaData()

    def _makeTable(self, symbol):
        return Table(
            'candles' + symbol.name, self.metadata,
            Column('id', Integer, primary_key=True),
            Column('opentime', DateTime),
            Column('open', Float),
            Column('high', Float),
            Column('low', Float),
            Column('close', Float),
            Column('closetime', DateTime),
            Column('trades', Integer),
            UniqueConstraint('opentime')
        )

    def _candleGenerator(self, symbol):
        client = Client(cfg.BINANCE_API_KEY, cfg.BINANCE_API_SECRET)
        return lambda sd, ed: client.get_historical_klines_generator(
            symbol.name, KLINE_INTERVAL_1MINUTE, str(sd), str(ed - minute)
        )

    def seed(self, symbol, sd, ed):
        conn = self.engine.connect()
        table = self._makeTable(symbol)
        table.create(self.engine, checkfirst=True)

        # clear data if table is marked dirty
        if not self.info.loadingCompleted(symbol):
            conn.execute(table.delete())
            self.info.clearData(symbol)

        # time frames in [sd, ed], where data is not in the database
        tframes = self.info.missingData(symbol, sd, ed)
        if tframes.is_empty(): return

        # set the database state to dirty to indicate loading unfinished
        self.info.setLoading(symbol, True)

        # seed the database with data from each candlegen
        candlegen = self._candleGenerator(symbol)
        iterations = sum((t.upper - t.lower) // minute for t in tframes)
        with tqdm(total=iterations, desc=symbol.name) as pb:
            
            for sd, ed in ((t.lower, t.upper) for t in tframes):
                top, tcp = None, None
                for i, candle in enumerate(candlegen(sd, ed)):

                    to = datetime.fromtimestamp(candle[0] / 1000, UTC)
                    tc = datetime.fromtimestamp(candle[6] / 1000, UTC)
                    sql_insert = table.insert().values(
                        opentime=to,
                        open=candle[1],
                        high=candle[2],
                        low=candle[3],
                        close=candle[4],
                        closetime=tc,
                        trades=candle[8]
                    )
                    
                    # fill if there is missing data
                    if i > 0:
                        dto = to - top
                        _to, _tc = top, tcp
                        for _ in range(dto // minute - 1):
                            _to += minute
                            _tc += minute
                            conn.execute(sql_insert.values(
                                opentime=_to, closetime=_tc
                            ))
                            pb.update(1)

                    conn.execute(sql_insert)
                    top, tcp = to, tc
                    pb.update(1)

        self.info.dataAdded(symbol, sd, ed)
        self.info.setLoading(symbol, False)

class CandleBrowser:
    
    def __enter__(self): 
        self.db = create_engine(cfg.DATABASE_SQLALCHEMY, echo=False)
        self.metadata = MetaData(bind=self.db)
        self.metadata.reflect(self.db)
        self.conn = self.db.connect()
        return self
    
    def __exit__(self, type, value, traceback):
        self.conn.close()
        self.db.dispose()

    def _getTable(self, symbol):
        return self.metadata.tables['candles' + symbol.name]

    def candlesByDate(self, symbol, sd, ed):
        table = self._getTable(symbol)
        sql_select = table.select().where(
            (sd <= table.c.opentime) & (table.c.opentime < ed)
        ).order_by(table.c.opentime)
        candles = self.conn.execute(sql_select)
        colnames = table.columns.keys()
        return DataFrame(dict(zip(colnames, zip(*candles))))
