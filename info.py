from pathlib import Path
from datetime import datetime
from json import load

from lib import DbInfoManager, config as cfg
from lib.cli import Argparser
from lib.enums import Symbol


argparser = Argparser()
args = argparser.parse_args()

info = DbInfoManager()
for sym in Symbol:
    intervals = info._loadIntervals(sym)
    trepr = ' & '.join([
        f'{interval.lower} - {interval.upper}'
        for interval in intervals
    ])
    print(sym.name + ':', trepr)
