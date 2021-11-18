from typing import List
from enum import Enum
from datetime import date, datetime, timedelta

from typer import Typer, Option

from lib import (
    CandleSeeder, CandleBrowser, CandleInfoManager, 
    BacktestEngine, strategies
)
from lib.enums import Symbol
from lib.graphics import drawHistory


app = Typer()

minute = timedelta(minutes=1)
isoday = date.today().isoformat()
isomonth = date.today().replace(day=1).isoformat()

symbol_names = [symbol.name for symbol in Symbol]
SymbolName = Enum('Sym', {s.name: s.name for s in Symbol})
getSymbols = lambda syms: [Symbol.__members__[sym.name] for sym in syms]
Strategy = Enum('Strategy', {s: s for s in strategies.names})

@app.command()
def info(symbol_names: List[SymbolName] = Option(symbol_names, '-sy')): 
    candle_info = CandleInfoManager()
    for symbol_name in symbol_names:
        print(candle_info.repr(symbol_name))

@app.command()
def seed(
    symbol_names: List[SymbolName],
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
    strategy_name: Strategy,
    symbol_names: List[SymbolName] = Option(symbol_names, '-sy'),
    start_date: datetime = Option(isomonth, '-sd'),
    end_date: datetime = Option(isoday, '-ed'),
    time_interval: int = Option(1, '-ti')
):
    # transform the arguments to the proper type
    dt = time_interval * minute
    symbols = getSymbols(symbol_names)
    strategy = strategies.getStrategy(strategy_name.name, symbols)

    # run strategy on the backtest engine
    engine = BacktestEngine(strategy)
    history, trades = engine.backtest(
        start_date, end_date, dt
    )

    # draw the history graph
    browser = CandleBrowser()
    drawHistory(browser, history, trades, start_date, end_date)
    
    print('max value:', history.max())
    print('min value:', history.min())
    print('end value:', history[-1])
    print('number of trades:', len(trades))

if __name__ == '__main__':  app()
