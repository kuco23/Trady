from typing import List
from enum import Enum
from datetime import date, datetime, timedelta

import typer

from lib import CandleSeeder, CandleBrowser, BacktestEngine
from lib.enums import Symbol
from lib.graphics import drawHistory
import strategies


minute = timedelta(minutes=1)

Sym = Enum('Sym', {sym.name: sym.name for sym in Symbol})
Strategies = Enum('Strategies', {s: s for s in strategies.strategies})

getStrategy = lambda name, symbols: getattr(strategies, name)(symbols)
getSymbols = lambda syms: [Symbol.__members__[sym.name] for sym in syms]
today = lambda: date.today().isoformat()

app = typer.Typer()

@app.command()
def seed(
    syms: List[Sym],
    start_date: datetime,
    end_date: datetime = today()
):
    symbols = getSymbols(syms)

    seeder = CandleSeeder()
    for symbol in symbols:
        seeder.seed(symbol, start_date, end_date)

@app.command()
def backtest(
    strategy_name: Strategies,
    syms: List[Sym],
    start_date: datetime,
    end_date: datetime = today(),
    time_interval: timedelta = minute
):
    symbols = getSymbols(syms)
    strategy = getStrategy(strategy_name, symbols)

    engine = BacktestEngine(strategy)
    history, trades = engine.backtest(
        start_date, end_date, time_interval
    )

    browser = CandleBrowser()
    drawHistory(browser, history, trades, start_date, end_date)

if __name__ == '__main__': 
    app()
