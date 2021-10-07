from datetime import datetime
from argparse import ArgumentParser

import matplotlib.pyplot as plt
import talib
from sqlalchemy import (
    MetaData, Table, Column,
    Integer, Float, String, DateTime,
    create_engine
)
from binance import Client
from binance.enums import KLINE_INTERVAL_1MINUTE

from lib import config as cfg

# todo: the date when trading on Binance began for a given symbol
sd_default = '1 Jan, 2017'

argparser = ArgumentParser()
argparser.add_argument('sym', type=str, metavar='symbol')
argparser.add_argument('-sd', type=str, metavar='start date')
argparser.add_argument('-ed', type=str, metavar='end date')
args = argparser.parse_args()

engine = create_engine(cfg.SQLALCHEMY_SQLITE, echo=True)
meta = MetaData()

candles = Table(
    'candles' + args.sym, meta,
    Column('id', Integer, primary_key=True),
    Column('opentime', DateTime),
    Column('closetime', DateTime),
    Column('open', Float),
    Column('close', Float),
    Column('high', Float),
    Column('low', Float),
    Column('trades', Integer)
)

candles.create(engine, checkfirst=True)
conn = engine.connect()
conn.execute(candles.delete()) # empty table

client = Client(cfg.BINANCE_API_KEY, cfg.BINANCE_API_SECRET)
candlegen = client.get_historical_klines_generator(
    symbol, KLINE_INTERVAL_1MINUTE, start_day or sd_default, args.ed
)

for candle in candlegen:
    opentime = datetime.fromtimestamp(candle[0] / 1000)
    closetime = datetime.fromtimestamp(candle[6] / 1000)
    sql_insert = candles.insert().values(
        opentime=opentime,
        closetime=closetime,
        open=candle[1],
        close=candle[4],
        high=candle[2],
        low=candle[3],
        symbol=args.sym
    )
    conn.execute(sql_insert)
