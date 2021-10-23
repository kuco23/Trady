from datetime import datetime
from time import sleep

from binance.client import Client
from binance.enums import *
from pandas import DataFrame

from lib import config as cfg
from lib.cli import Argparser
from lib.enums import BinanceCandle, Trade
from lib.exceptions import InvalidPosition, OrderFillTimeout
from lib.models import AbstractData, TradeRecord
from lib.strategies import *


class Data(AbstractData):
    _candleattr = [e.name for e in BinanceCandle]
    
    def __init__(self, client):
        self.client = client

    def candles(self, symbol, ncandles):
        candles = self.client.get_klines(
            symbol=symbol.name,
            interval=KLINE_INTERVAL_1MINUTE,
            limit=ncandles
        )
        return DataFrame(dict(zip(self._candleattr, candles)))

    def price(self, symbol):
        return self.client.get_avg_price(symbol)['price']

def getAssets(client):
    account_data = client.get_account()
    return {
        balance['asset']: balance['free']
        for balance in account_data['balances']
    }

if __name__ == '__main__':

    argparser = Argparser()
    argparser.add_argument_strategy()
    argparser.add_argument_time_interval()
    args = argparser.parse_args()

    client = Client(cfg.BINANCE_API_KEY, cfg.BINANCE_API_SECRET)

    data = Data(client)
    state = {'assets': getAssets(client), 'actions': []}
    history = []

    while True:
        args.strategy(data, state)
        while state['actions']:
            action = state['actions'].pop()
            base, quote = action.symbol.value
            price = data.price(action.symbol)

            assets = state['assets']
            order_filled = False
            if action.trade == Trade.BUY:
                resp = client.order_market_buy(
                    symbol=action.symbol,
                    quantity=action.quantity
                )
                order_filled = resp['status'] == 'FILLED'
                order_id = resp['id']
            elif action.trade == Trade.SELL:
                resp = client.order_market_sell(
                    symbol=action.symbol,
                    quantity=action.quantity
                )
                order_filled = resp['status'] == 'FILLED'
                order_id = resp['id']
            else: raise InvalidPosition(action.trade)

            history.append(TradeRecord(
                datetime.now(), action.trade,
                action.symbol, action.quantity, price
            ))
               
            slept = 0
            while not order_filled:
                sleep(2)
                slept += 2
                if mt > args.si: raise OrderFillTimeout()
                order = client.get_order(
                    symbol=action.symbol,
                    orderId=order_id
                )
                order_filled = order['status'] == 'FILLED'

            state['assets'] = getAssets(client)
            print(base, state['assets'][base])
            print(quote, state['assets'][quote])
            sleep(args.si.seconds - slept)
            
