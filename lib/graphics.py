from pandas import DataFrame
from matplotlib import pyplot as plt
from sqlalchemy import create_engine, MetaData

from . import config as cfg
from .enums import Trade, Symbol

symbol = Symbol.ADAUSDT

engine = create_engine(cfg.SQLALCHEMY_SQLITE, echo=False)
metadata = MetaData(bind=engine)
metadata.reflect(engine)
conn = engine.connect()

def drawHistory(history):
    times = [h[0] for h in history]
    s, t = min(times), max(times)
    table = metadata.tables['candles' + symbol.name]
    sql_select = table.select().where(
        (s < table.c.opentime) & (table.c.opentime <= t)
    )
    candles = conn.execute(sql_select)
    df = DataFrame(dict(zip(table.columns.keys(), zip(*candles))))

    plt.plot(df.opentime, df.open)
    plt.show()
    
