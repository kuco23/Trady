from pathlib import Path
from datetime import datetime
from json import load

from lib import DbInfo, config as cfg
from lib.cli import Argparser


def availableCandles(symbol):
    path = Path(cfg.DATA_PATH_META)
    if not path.exists(): return
    with open(path, 'r') as file:
        data = load(file)
    return data.get(symbol.name)

argparser = Argparser()
argparser.add_argument_symbol()
args = argparser.parse_args()

info = DbInfo()
for sd, ed in info._loadIntervals(args.symbol):
    print(sd, ed)
