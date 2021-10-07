from types import SimpleNamespace
from time import sleep
from datetime import datetime, timedelta

import numpy as np
from binance.client import Client
from binance.enums import *

from lib import config as cfg
from lib.strategies import meanRevisionTrend

money = 100
symbol = 'ETHUSDT'
date_start = [2021, 1, 1]
date_end = [2021, 3, 1]
interval = {'minutes': 5}
strategy = meanRevisionTrend

client = Client(cfg.BINANCE_API_KEY, cfg.BINANCE_API_SECRET)

now = datetime(*date_start)
end = datetime(*date_end)
fivemin = timedelta(**interval)
oneday = timedelta(days=1)
onehour = timedelta(hours=1)

state = SimpleNamespace(has_position=False, usdt=money, crypto=0)
while now < end:
    tsp_now = str(now.timestamp())
    tsp_mday = str((now - oneday).timestamp())
    tsp_mhour = str((now - onehour).timestamp())
    
    klines_1day = client.get_historical_klines(
        symbol, KLINE_INTERVAL_5MINUTE,
        tsp_mday, tsp_now
    )
    klines_1hour = client.get_historical_klines(
        symbol, KLINE_INTERVAL_5MINUTE,
        tsp_mhour, tsp_now
    )
    prices_1day = [k[1] for k in klines_1day]
    prices_1hour = [k[1] for k in klines_1hour]

    pos = meanRevisionTrend(
        np.asarray(prices_1day, dtype=float),
        np.asarray(prices_1hour, dtype=float),
        state
    )
    
    if pos == 'buy':
        state.has_position = True
        state.crypto = state.usdt / prices_1hour[-1]
        state.usdt = 0
    elif pos == 'sell':
        state.has_position = False
        state.usdt = state.crypto * prices_1hour[-1]
        state.crypto = 0
        
    sleep(0.1)
    print(state)
