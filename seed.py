from argparse import ArgumentParser
from datetime import date, datetime, timedelta

from sqlalchemy import (
    MetaData, Table, Column,
    Integer, Float, String, DateTime,
    create_engine
)
from binance import Client
from binance.enums import KLINE_INTERVAL_1MINUTE

from lib import config as cfg
from lib.enums import Symbol

yesterday = date.today() - timedelta(days=1)
month = yesterday.strftime('%b')

argparser = ArgumentParser()
argparser.add_argument(
    'sym', type=str, metavar='symbol',
    choices=[symbol.name for symbol in Symbol]
)
argparser.add_argument(
    '-sd', type=str, metavar='start date',
    default='1 jan, 2017' # soon enough
)
argparser.add_argument(
    '-ed', type=str, metavar='end date',
    default=f'{yesterday.day} {month}, {yesterday.year}'
)
argparser.add_argument('-eo', type=str, metavar='sql echo')
args = argparser.parse_args()

echo = args.eo is not None
engine = create_engine(cfg.SQLALCHEMY_SQLITE, echo=echo)
meta = MetaData()

candle_table = Table(
    'candles' + args.sym, meta,
    Column('id', Integer, primary_key=True),
    Column('opentime', DateTime),
    Column('open', Float),
    Column('high', Float),
    Column('low', Float),
    Column('close', Float),
    Column('closetime', DateTime),
    Column('trades', Integer)
)

candle_table.create(engine, checkfirst=True)
conn = engine.connect()
conn.execute(candle_table.delete()) # empty table

client = Client(cfg.BINANCE_API_KEY, cfg.BINANCE_API_SECRET)
candlegen = client.get_historical_klines_generator(
    args.sym, KLINE_INTERVAL_1MINUTE, args.sd, args.ed
)

minute = timedelta(minutes=1)
top, tcp = None, None
for i, candle in enumerate(candlegen):
    
    to = datetime.fromtimestamp(candle[0] / 1000)
    tc = datetime.fromtimestamp(candle[6] / 1000)
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
        if dto // minute > 1: print(dto // minute)
        for _ in range(dto // minute - 1):
            _to += minute
            _tc += minute
            conn.execute(sql_insert.values(
                opentime=_to, closetime=_tc
            ))

    conn.execute(sql_insert)
    top, tcp = to, tc
    
    if i % 100 == 0: print(i)
