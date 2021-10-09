from argparse import ArgumentParser
from datetime import datetime

from matplotlib import pyplot as plt
import talib
from sqlalchemy import (
    MetaData, Table, Column,
    Integer, Float, String, DateTime,
    create_engine
)
from binance import Client
from binance.enums import KLINE_INTERVAL_1MINUTE

from lib import config as cfg
from lib.enums import Symbol

# todo: the date when trading on Binance began for a given symbol
sd_default = '1 Jan, 2017'

argparser = ArgumentParser()
argparser.add_argument(
    'sym', type=str, metavar='symbol',
    options=[symbol.name for sym in Symbol]
)
argparser.add_argument('-sd', type=str, metavar='start date')
argparser.add_argument('-ed', type=str, metavar='end date')
argparser.add_argument('-eo', type=str, metavar='sql echo')
args = argparser.parse_args()

engine = create_engine(cfg.SQLALCHEMY_SQLITE, echo=args.eo is not None)
meta = MetaData()

candles = Table(
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

candles.create(engine, checkfirst=True)
conn = engine.connect()
conn.execute(candles.delete()) # empty table

client = Client(cfg.BINANCE_API_KEY, cfg.BINANCE_API_SECRET)
candlegen = client.get_historical_klines_generator(
    args.sym, KLINE_INTERVAL_1MINUTE, args.sd or sd_default, args.ed
)

for i, candle in enumerate(candlegen):
    opentime = datetime.fromtimestamp(candle[0] / 1000)
    closetime = datetime.fromtimestamp(candle[6] / 1000)
    sql_insert = candles.insert().values(
        opentime=opentime,
        open=candle[1],
        high=candle[2],
        low=candle[3],
        close=candle[4],
        closetime=closetime,
        trades=candle[8]
    )
    conn.execute(sql_insert)
