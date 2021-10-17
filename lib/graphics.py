from datetime import timedelta

from pandas import DataFrame, Series
from matplotlib import pyplot as plt
from sqlalchemy import create_engine, MetaData

from . import config as cfg
from .enums import Trade, Symbol

symbol = Symbol.SHIBUSDT

def getAx(title, xlab, ylab):
    fig, ax = plt.subplots(1, 1, figsize=(15, 8))
    ax.set_title(title)
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_alpha(0.5)
    ax.spines['bottom'].set_alpha(0.5)
    ax.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.5)
    return ax

def drawHistory(data, history, sd, se):
    candles = data._candlesByDate(symbol, sd, se)
    buys = ((h[0], h[3]) for h in history if h[1] == Trade.BUY)
    sells = ((h[0], h[3]) for h in history if h[1] == Trade.SELL)
    ax = getAx('history', 'datetime', symbol.name)
    ax.plot(candles.opentime, candles.open, zorder=0)
    ax.scatter(*zip(*buys), color='green', zorder=1)
    ax.scatter(*zip(*sells), color='red', zorder=1)
    plt.show()
    
