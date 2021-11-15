import os
from pytz import UTC
from datetime import datetime, timedelta
from json import dump, load
from pathlib import Path

from binance import Client
from binance.enums import KLINE_INTERVAL_1MINUTE
from sqlalchemy import (Column, DateTime, Float, Integer, MetaData, Table,
                        UniqueConstraint, create_engine)
from tqdm import tqdm

from lib import DbInfoManager, config as cfg
from lib.cli import Argparser


minute = timedelta(minutes=1)

argparser = Argparser()
argparser.add_argument_symbol()
argparser.add_argument_start_date()
argparser.add_argument_end_date()
args = argparser.parse_args()

# set up orm objects
meta = MetaData()
candle_table = Table(
    'candles' + args.symbol.name, meta,
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
engine = create_engine(cfg.SQLALCHEMY_SQLITE)
candle_table.create(engine, checkfirst=True)
conn = engine.connect()

# check the state of the symbol's database table
info = DbInfoManager()
if info.loadingCompleted(args.symbol):
    conn.execute(candle_table.delete())
    info.clearData(args.symbol)
info.setLoading(args.symbol, True)

# get timeframes not already in the database for symbol
tframes = info.missingData(args.symbol, args.sd, args.ed)
if tframes.is_empty(): os._exit(0)

# set the candle generator via binance api
client = Client(cfg.BINANCE_API_KEY, cfg.BINANCE_API_SECRET)
candlegen = lambda sd, ed: client.get_historical_klines_generator(
    args.symbol.name, KLINE_INTERVAL_1MINUTE, str(sd), str(ed - minute)
)

# seed the database with data from each candlegen
iterations = sum((t.upper - t.lower) // minute for t in tframes)
with tqdm(total=iterations) as pb:
    
    for sd, ed in ((t.lower, t.upper) for t in tframes):
        top, tcp = None, None
        for i, candle in enumerate(candlegen(sd, ed)):

            to = datetime.fromtimestamp(candle[0] / 1000, UTC)
            tc = datetime.fromtimestamp(candle[6] / 1000, UTC)
            sql_insert = candle_table.insert().values(
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

info.dataAdded(args.symbol, args.sd, args.ed)
info.setLoading(args.symbol, False)
