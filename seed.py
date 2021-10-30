from datetime import datetime, timedelta
from json import dump, load
from pathlib import Path

from binance import Client
from binance.enums import KLINE_INTERVAL_1MINUTE
from sqlalchemy import (Column, DateTime, Float, Integer, MetaData, Table,
                        create_engine)
from tqdm import tqdm

from lib import DbInfo, config as cfg
from lib.cli import Argparser


minute = timedelta(minutes=1)
tfm = '%Y-%m-%d %H:%M:%S'

argparser = Argparser()
argparser.add_argument_symbol()
argparser.add_argument_start_date()
argparser.add_argument_end_date()
args = argparser.parse_args()

info = DbInfo()
intervals = info.removedIntervals(args.symbol, args.sd, args.ed)

client = Client(cfg.BINANCE_API_KEY, cfg.BINANCE_API_SECRET)
candlegen = lambda sd, ed: client.get_historical_klines_generator(
    args.symbol.name, KLINE_INTERVAL_1MINUTE,
    sd.strftime(tfm), (ed - minute).strftime(tfm)
)

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
    Column('trades', Integer)
)
engine = create_engine(cfg.SQLALCHEMY_SQLITE)
candle_table.create(engine, checkfirst=True)
conn = engine.connect()

iterations = sum((ed - sd) // minute for sd, ed in intervals)
with tqdm(total=iterations) as pb:
    
    for sd, ed in intervals:
        top, tcp = None, None
        for i, candle in enumerate(candlegen(sd, ed)):
            
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

info.addInterval(args.symbol, args.sd, args.ed)
