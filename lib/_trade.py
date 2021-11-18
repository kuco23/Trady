from datetime import datetime
from time import sleep

from binance.client import Client
from binance.enums import *
from pandas import DataFrame

from . import cfg
from .enums import BinanceCandle, Trade
from .exceptions import InvalidPosition, OrderFillTimeout
from .models import AbstractData, TradeRecord


class LiveData(AbstractData):
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
        

class TradeEngine:

    def __init__(self, strategy):
        self.strategy = strategy
        self.client = Client(
            cfg.BINANCE_API_KEY, 
            cfg.BINANCE_API_SECRET
        )
    
    def assets(self):
        account_data = self.client.get_account()
        return {
            balance['asset']: float(balance['free'])
            for balance in account_data['balances']
        }
    
    def trade(self, ti):
        data = LiveData(self.client)
        state = {'assets': self.assets(), 'actions': []}

        trades, history = [], []
        while True:
            self.strategy(data, state)
            slept = 0
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
                    resp = self.client.order_market_buy(
                        symbol=action.symbol,
                        quantity=quantity
                    )
                elif action.trade == Trade.SELL:
                    resp = self.client.order_market_sell(
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
                    sleep(0.5)
                    slept += 0.5
                    if slept > ti.seconds: raise OrderFillTimeout()
                    order = self.client.get_order(
                        symbol=action.symbol,
                        orderId=order_id
                    )
                    order_filled = order['status'] == 'FILLED'

                state['assets'] = self.assets()

            history.append(data.portfolioValue(state['assets']))

            print('portfolio value:', history[-1])

            sleep(ti.seconds - slept)
    