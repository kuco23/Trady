from matplotlib import pyplot as plt

from . import CandleBrowser
from .enums import Trade


def _configAx(ax, title, xlab, ylab):
    ax.set_title(title)
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_alpha(0.5)
    ax.spines['bottom'].set_alpha(0.5)
    ax.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.5)

def drawTradeHistory(history, trades, sd, ed):
    assert len(trades) > 0
    symbol = trades[0].symbol

    #buys = ((r.time, r.price) for r in trades if r.trade == Trade.BUY)
    #sells = ((r.time, r.price) for r in trades if r.trade == Trade.SELL)

    with CandleBrowser() as browser: 
        candles = browser.candlesByDate(symbol, sd, ed)
    
    fig, (ax1, ax2) = plt.subplots(2, figsize=(15, 8))
    fig.suptitle('trades / portfolio value')
    _configAx(ax1, '', 'datetime', symbol.name)
    _configAx(ax2, '', 'datetime', 'USDT')
    ax1.plot(candles.opentime, candles.open, zorder=0)
    #ax1.scatter(*zip(*buys), color='green', zorder=1)
    #ax1.scatter(*zip(*sells), color='red', zorder=1)
    ax2.plot(candles.opentime, history, zorder=2)
    plt.show()
    
