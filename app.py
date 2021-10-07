from datetime import datetime

from binance.client import Client
from binance.enums import *

from lib import config as cfg

# get_klines(symbol=, interval=)
'''
[
    [
        1499040000000,      # Open time
        "0.01634790",       # Open
        "0.80000000",       # High
        "0.01575800",       # Low
        "0.01577100",       # Close
        "148976.11427815",  # Volume
        1499644799999,      # Close time
        "2434.19055334",    # Quote asset volume
        308,                # Number of trades
        "1756.87402397",    # Taker buy base asset volume
        "28.46694368",      # Taker buy quote asset volume
        "17928899.62484339" # Can be ignored
    ]
]
'''

# get_exchange_info() -> valid symbols ['symbols']
# get_account()
# get_asset_balance(asset, **kwargs)
# get_trade_fee(**kwargs)

# order_market_sell(symbol=, quantity=) -> sell quantity symbol[0] for symbol[1]
# order_market_buy(symbol=, quantity=) -> buy quantity symbol[0] for symbol[1]

client = Client(cfg.BINANCE_API_KEY, cfg.BINANCE_API_SECRET)

