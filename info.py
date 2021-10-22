from pathlib import Path
from datetime import datetime
from json import load

from lib import config as cfg
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

interval = availableCandles(args.symbol)
if interval is not None:
    for key in interval.keys():
        print(key, datetime.fromtimestamp(interval[key]))
