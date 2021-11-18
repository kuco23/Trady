from typing import List
from enum import Enum
from datetime import date, datetime, timedelta

from typer import Typer, Option

from lib import CandleSeeder, CandleBrowser, BacktestEngine
from lib.enums import Symbol
from lib.graphics import drawHistory
import strategies


minute = timedelta(minutes=1)

Sym = Enum('Sym', {sym.name: sym.name for sym in Symbol})
strategy_names = [s.stem for s in strategies.strategy_paths]
Strategy = Enum('Strategies', {s: s for s in strategies})

getStrategy = lambda name, symbols: getattr(strategies, name)(symbols)
getSymbols = lambda syms: [Symbol.__members__[sym.name] for sym in syms]
today = lambda: date.today().isoformat()

app = Typer()

@app.command()
def seed(
    symbol_names: List[Sym],
    start_date: Option(datetime, "-sd"),
    end_date: datetime = Option(today(), "-ed")
):
    symbols = getSymbols(symbol_names)

    seeder = CandleSeeder()
    for symbol in symbols:
        seeder.seed(symbol, start_date, end_date)

@app.command()
def backtest(
    strategy_name: Strategy,
    symbol_names: List[Sym],
    start_date: Option(datetime, "-sd"),
    end_date: datetime = Option(today(), "-ed"),
    time_interval: timedelta = Option(minute, "-ti")
):
    symbols = getSymbols(symbol_names)
    strategy = getStrategy(strategy_name, symbols)

    engine = BacktestEngine(strategy)
    history, trades = engine.backtest(
        start_date, end_date, time_interval
    )

    browser = CandleBrowser()
    drawHistory(browser, history, trades, start_date, end_date)

if __name__ == '__main__': 
    app()
