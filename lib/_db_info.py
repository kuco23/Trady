from pathlib import Path
from json import load, dump
from datetime import datetime as dt, timedelta as td

import intervals as I

from . import config as cfg
from .enums import Symbol


"""
The dbInfoManager is an object interface to "info.json",
which describes the candle data in the "candles.db" database.
Mainly it describes the datetime intervals, during which the
candles are available for a given symbol.
"""

class DbInfoManager: 

    def __init__(self):
        self.path = Path(cfg.INFO_PATH)
        self._load()
        self._fillSymbolInfo()

    def _infoTemplate(self, symbol):
        return {'sd': [], 'ed': [], 'loading': False}

    def _fillSymbolInfo(self):
        for symbol in Symbol:
            if symbol.name in self._info: continue
            self._info[symbol.name] = self._infoTemplate(symbol)

    def _load(self):
        if self.path.is_file():
            with open(self.path, 'r') as file:
                self._info = load(file)
        else: self._info = dict()

    def _save(self):
        if not self.path.is_file():
            with open(self.path, 'a') as file: pass
        with open(self.path, 'w') as file:
            dump(self._info, file)

    def _loadIntervals(self, symbol):
        if symbol.name not in self._info.keys():
            self._addSymbolTemplate(symbol)
        intervals = I.empty()
        syminfo = self._info[symbol.name]
        for sd, ed in zip(syminfo['sd'], syminfo['ed']):
            sdi, edi = map(dt.fromtimestamp, [sd, ed])
            intervals |= I.closedopen(sdi, edi)
        return intervals

    def _saveIntervals(self, symbol, intervals):
        syminfo = self._info[symbol.name]
        sd, ed = syminfo['sd'], syminfo['ed']
        sd.clear()
        ed.clear()
        for interval in intervals:
            sd.append(interval.lower.timestamp())
            ed.append(interval.upper.timestamp())
        self._save()

    def clearData(self, symbol):
        self._info[symbol.name] = self._infoTemplate(symbol)
        self._save()

    # to figure out which parts are missing when wanting
    # to get [sd, ed) interval of new candle data
    def missingData(self, symbol, sd, ed):
        interval = I.closedopen(sd, ed)
        intervals = self._loadIntervals(symbol)
        return interval - intervals

    # adding interval [sd, ed) of new candle data to info.json
    def dataAdded(self, symbol, sd, ed):
        interval = I.closedopen(sd, ed)
        intervals = self._loadIntervals(symbol)
        self._saveIntervals(symbol, interval | intervals)

    # checking if the interval is included in the database
    def hasData(self, symbol, sd, ed):
        interval = I.closedopen(sd, ed)
        intervals = self._loadIntervals(symbol)
        return intervals.contains(interval)

    def setLoading(self, symbol, is_loading):
        self._info[symbol.name]['loading'] = is_loading
        self._save()

    def loadingCompleted(self, symbol):
        return self._info[symbol.name]['loading']
