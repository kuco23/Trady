from typing import List
from enum import Enum
from datetime import date, datetime, timedelta

from typer import Typer, Option

from lib import (
    CandleSeeder, CandleInfoManager, 
    BacktestEngine, TradeEngine, strategies
)
from lib.enums import Symbol
from lib.graphics import drawTradeHistory


app = Typer()

minute = timedelta(minutes=1)
isoday = date.today().isoformat()
isomonth = date.today().replace(day=1).isoformat()

StrategyChoice = Enum('StrategyChoice', {
    s: s for s in strategies.names
})
SymbolChoice = Enum('SymbolChoice', {
    **{s.name: s.name for s in Symbol}, 
    **{'ALL': 'ALL', 'LOAD': 'LOAD'}
})
getSymbols = lambda syms: [
    Symbol.__members__[sym.name] for sym in syms
] if syms[0].name != 'ALL' else list(Symbol)

@app.command()
def info(symbol_names: List[SymbolChoice]):
    symbols = getSymbols(symbol_names)
    candle_info = CandleInfoManager()
    for symbol_name in symbols:
        print(candle_info.repr(symbol_name))

@app.command()
def seed(
    symbol_names: List[SymbolChoice],
    start_date: datetime = Option(isomonth, '-sd'),
    end_date: datetime = Option(isoday, '-ed')
):
    symbols = getSymbols(symbol_names)
    # seed for each symbol
    seeder = CandleSeeder()
    for symbol in symbols:
        seeder.seed(symbol, start_date, end_date)

@app.command()
def backtest(
    strategy_name: StrategyChoice,
    symbol_names: List[SymbolChoice],
    start_date: datetime = Option(isomonth, '-sd'),
    end_date: datetime = Option(isoday, '-ed'),
    time_interval: int = Option(1, '-ti')
):
    # transform the arguments to the proper type
    dt = time_interval * minute
    symbols = getSymbols(symbol_names)
    strategy = strategies.getStrategy(
        strategy_name.name, symbols
    )

    # run strategy on the backtest engine
    engine = BacktestEngine(strategy)
    history, trades = engine.backtest(
        start_date, end_date, dt
    )

    # draw the history graph
    drawTradeHistory(history, trades, start_date, end_date)
    
    # print the relevant info
    print('max value:', history.max())
    print('min value:', history.min())
    print('end value:', history[-1])
    print('number of trades:', len(trades))

@app.command() 
def trade(
    strategy_name: StrategyChoice,
    symbol_names: List[SymbolChoice],
    time_interval: int = Option(1, '-ti')
):
    # transform the arguments to the proper type
    dt = time_interval * minute
    symbols = getSymbols(symbol_names)
    strategy = strategies.getStrategy(
        strategy_name.name, symbols
    )

    # run strategy on the trade engine
    engine = TradeEngine(strategy)
    engine.trade(dt) 

if __name__ == '__main__':  app()
