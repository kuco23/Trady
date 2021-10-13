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

def drawHistory(sd, se, history):
    table = metadata.tables['candles' + symbol.name]
    sql_select = table.select().where(
        (sd < table.c.opentime) & (table.c.opentime <= se)
    )
    candles = conn.execute(sql_select)
    df = DataFrame(dict(zip(table.columns.keys(), zip(*candles))))

    plt.plot(df.opentime, df.open)
    plt.show()
    
