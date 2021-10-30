from pathlib import Path
from json import load, dump
from datetime import datetime as dt, timedelta as td

from . import config as cfg


"""
The DbInfo is responsible for describing the dates
of symbols in the database. The form of the info.json file is
{
symbol_name: {
    "start_dates": [sd1, ..., sdn],
    "end_dates": [ed1, ..., edn]
}
"""

class DbInfo:
    _minute = td(minutes=1)
    _day = td(days=1)

    def __init__(self):
        self.path = Path(cfg.INFO_PATH)
        self._load()

    def _load(self):
        if self.path.is_file():
            with open(self.path, 'r') as file:
                self._info = load(file)
        else: self._info = dict()

    def _dump(self):
        if not self.path.is_file():
            with open(self.path, 'a') as file: pass
        with open(self.path, 'w') as file:
            dump(self._info, file)

    def _addSymbolTemplate(self, symbol):
        self._info[symbol.name] = {'sd': [], 'ed': []}

    def _saveIntervals(self, symbol, intervals):
        syminfo = self._info[symbol.name]
        sd, ed = syminfo['sd'], syminfo['ed']
        sd.clear()
        ed.clear()
        for sdi, edi in intervals:
            sd.append(sdi.timestamp())
            ed.append(edi.timestamp())

    def _loadIntervals(self, symbol):
        if symbol.name not in self._info.keys():
            self._addSymbolTemplate(symbol)
        syminfo = self._info[symbol.name]
        for sd, ed in zip(syminfo['sd'], syminfo['ed']):
            sdi, edi = map(dt.fromtimestamp, [sd, ed])
            yield sdi, edi

    # merge the interval [sd, ed] into list(self._intervals)
    def _mergeInterval(self, symbol, sd, ed):
        sdr, edr, overlap, touched = sd, ed, False, False
        intervals = []
        for sdi, edi in self._loadIntervals(symbol):
            # [sd, ed] \cap [sdi, edi] = \emptyset
            if sdi < sd and edi < sd or sdi > ed and edi > ed:
                intervals.append([sdi, edi])
                continue
            # sd \in [sd, ed] \cap [sdi, edi]
            if not overlap and sd <= sdi or sd <= edi:
                overlap = touched = True
                sdr = min(sd, sdi)
            # ed \in [sd, ed] \cap [sdi, edi]
            if overlap and ed <= edi:
                overlap = False
                edr = edi
                intervals.append([sdr, edr])
        # if ed > edi for all edi or
        # [sd, ed] was disjunct to all [sdi, edi]
        if overlap or not touched: intervals.append([sdr, ed])
        return intervals

    def removedIntervals(self, symbol, sd, ed):
        holes = []
        for sdi, edi in self._loadIntervals(symbol):
            if sd < sdi: holes.append([sd, sdi])
            sd = edi
            if ed <= edi: break
        else: holes.append([sd, ed])
        return holes

    def addInterval(self, symbol, sd, ed):
        intervals = self._mergeInterval(symbol, sd, ed)
        self._saveIntervals(symbol, intervals)
        self._dump()
