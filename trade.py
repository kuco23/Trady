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
from strategies import *


class Data(AbstractData):
    _candleattr = [e.value[0] for e in BinanceCandle]
    _candletype = [e.value[1] for e in BinanceCandle]
    
    def __init__(self, client):
        self.client = client

    def candles(self, symbol, ncandles):
        resp = self.client.get_klines(
            symbol=symbol.name,
            interval=KLINE_INTERVAL_1MINUTE,
            limit=ncandles
        )
        candles = [
            [tp(c) for tp, c in zip(self._candletype, row)]
            for row in resp
        ]
        return DataFrame(dict(zip(self._candleattr, zip(*candles))))

    def price(self, symbol):
        return self.candles(symbol,1).close.iloc[-1]
        

    def assets(self):
        account_data = self.client.get_account()
        return {
            balance['asset']: float(balance['free'])
            for balance in account_data['balances']
        }

if __name__ == '__main__':

    argparser = Argparser()
    argparser.add_argument_strategy()
    argparser.add_argument_time_interval()
    args = argparser.parse_args()

    client = Client(cfg.BINANCE_API_KEY, cfg.BINANCE_API_SECRET)

    data = Data(client)
    state = {'assets': data.assets(), 'actions': []}
    trades, history = [], []

    while True:
        slept = 0
        args.strategy(data, state)
        while state['actions']:
            action = state['actions'].pop()
            assets = state['assets']
            base, quote = action.symbol.value
            price = data.price(action.symbol)

            if action.quantity is not None:
                quantity = action.quantity
            elif action.trade == Trade.BUY:
                quantity = assets[quote] * action.ratio
            elif action.trade == Trade.SELL:
                quantity = assets[base] * action.ratio

            if action.trade == Trade.BUY:
                resp = client.order_market_buy(
                    symbol=action.symbol,
                    quantity=quantity
                )
            elif action.trade == Trade.SELL:
                resp = client.order_market_sell(
                    symbol=action.symbol,
                    quantity=quantity
                )
            else: raise InvalidPosition(action.trade)
            
            order_filled = resp['status'] == 'FILLED'
            order_id = resp['id']

            trades.append(TradeRecord(
                datetime.now(), action.trade,
                action.symbol, quantity, price
            ))

            print(trades[-1])
            
            while not order_filled:
                sleep(0.3)
                slept += 1
                if slept > 10: raise OrderFillTimeout()
                order = client.get_order(
                    symbol=action.symbol,
                    orderId=order_id
                )
                order_filled = order['status'] == 'FILLED'

            state['assets'] = data.assets()

        history.append(data.portfolioValue(state['assets']))

        print('portfolio value:', history[-1])

        sleep(args.ti.seconds)
            
