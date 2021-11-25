from copy import deepcopy
from datetime import datetime
from time import sleep
from requests.exceptions import ConnectionError, ReadTimeout

from binance.client import Client
from binance.enums import KLINE_INTERVAL_1MINUTE
from pandas import DataFrame

from . import cfg
from .enums import BinanceCandle, Trade
from .exceptions import OrderFillTimeout
from .models import AbstractData, TradeRecord, state_template


fee = 0.001 # binance max fee
q = 1 - fee

connection_retry_period = 0.5
order_check_period = 0.5

def forceResponse(fun):
    def wrapper(*args):
        while True:
            try: return fun(*args)
            except ConnectionError as e: 
                print('handled exception', e)
            except ReadTimeout as e:
                print('handled exception', e)
            sleep(connection_retry_period)
    return wrapper

class LiveData(AbstractData):
    _candleattr = [e.value[0] for e in BinanceCandle]
    _candletype = [e.value[1] for e in BinanceCandle]
    
    def __init__(self, client):
        self.client = client

    @forceResponse
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


class TradeEngine:

    def __init__(self, strategy):
        self.strategy = strategy
        self.client = Client(
            cfg.BINANCE_API_KEY, 
            cfg.BINANCE_API_SECRET
        )
    
    @forceResponse
    def _lastprice(self, symbol):
        last_trade = self.client.get_recent_trades(
            symbol=symbol.name, limit=1
        )[0]
        return float(last_trade['price'])

    @forceResponse
    def _orderTradeAction(self, action):
        action.price = self._lastprice(action.symbol)
        match action.trade:
            case Trade.BUY: 
                return self.client.order_market_buy(
                    symbol=action.symbol.name,
                    quantity=action.iquantity * q
                )
            case Trade.SELL:
                return self.client.order_market_sell(
                    symbol=action.symbol.name,
                    quantity=action.iquantity * q
                )
    
    @forceResponse
    def assets(self):
        account_data = self.client.get_account()
        return {
            balance['asset']: float(balance['free'])
            for balance in account_data['balances']
        }
    
    def trade(self, ti):
        data = LiveData(self.client)
        state = deepcopy(state_template)
        state['assets'] = self.assets()

        trades, history = [], []
        while True:
            self.strategy(data, state)
            slept = 0
            while state['actions']:
                action = state['actions'].pop()
                action.setQuantityFromRatio(state['assets'])

                order = self._orderTradeAction(action)
                price = order['fills'][0]['price']
                quantity = order['cummulativeQuoteQty']

                # wait until the order is filled
                while order['status'] != 'FILLED':
                    if slept + order_check_period > ti.seconds:
                        raise OrderFillTimeout()
                    sleep(order_check_period)
                    slept += order_check_period
                    order = self.client.get_order(
                        symbol=action.symbol,
                        orderId=order['orderId']
                    )

                # TODO
                # calculate from the order to avoid the
                # overhead and connection issues
                state['assets'] = self.assets()

                trades.append(TradeRecord(
                    datetime.now(), action.trade, 
                    action.symbol, quantity, price
                ))
                print(trades[-1])

            history.append(data.portfolioValue(state['assets']))
            print('portfolio value:', history[-1])

            sleep(ti.seconds - slept)
    