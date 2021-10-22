from datetime import datetime, timedelta
from json import dump, load
from pathlib import Path

from binance import Client
from binance.enums import KLINE_INTERVAL_1MINUTE
from sqlalchemy import (Column, DateTime, Float, Integer, MetaData, Table,
                        create_engine)
from tqdm import tqdm

from lib import config as cfg
from lib.cli import Argparser


def binanceDateFormat(date):
    month = date.strftime('%b')
    return f'{date.day} {month}, {date.year}'

argparser = Argparser()
argparser.add_argument_symbol()
argparser.add_argument_start_date()
argparser.add_argument_end_date()
args = argparser.parse_args()

meta = MetaData()
engine = create_engine(cfg.SQLALCHEMY_SQLITE)

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

candle_table.create(engine, checkfirst=True)
conn = engine.connect()
conn.execute(candle_table.delete()) # empty table

client = Client(cfg.BINANCE_API_KEY, cfg.BINANCE_API_SECRET)
candlegen = client.get_historical_klines_generator(
    args.symbol.name, KLINE_INTERVAL_1MINUTE,
    binanceDateFormat(args.sd),
    binanceDateFormat(args.ed)
)

top, tcp = None, None
minute = timedelta(minutes=1)
iterations = (args.ed - args.sd) // minute
progressbar = tqdm(total=iterations)
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
        for _ in range(dto // minute - 1):
            _to += minute
            _tc += minute
            conn.execute(sql_insert.values(
                opentime=_to, closetime=_tc
            ))
            progressbar.update(1)

    conn.execute(sql_insert)
    top, tcp = to, tc
    progressbar.update(1)

# log timeframe in which the candles 
# are available for symbol
path = Path(cfg.DATA_PATH_META)
if path.is_file():
    with open(path, 'r') as file:
        metalog = load(file)
else: metalog = dict()
with open(path, 'w') as file:
    metalog[args.symbol.name] = {
        'sd': args.sd.timestamp(),
        'ed': args.ed.timestamp()
    }
    dump(metalog, file)
