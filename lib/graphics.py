from matplotlib import pyplot as plt

from .enums import Trade


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
    symbol = history[0].symbol
    candles = data._candlesByDate(symbol, sd, se)
    buys = ((r.time, r.price) for r in history if r.trade == Trade.BUY)
    sells = ((r.time, r.price) for r in history if r.trade == Trade.SELL)
    ax = getAx('history', 'datetime', symbol.name)
    ax.plot(candles.opentime, candles.open, zorder=0)
    ax.scatter(*zip(*buys), color='green', zorder=1)
    ax.scatter(*zip(*sells), color='red', zorder=1)
    plt.show()
    
