import numpy as np

def varianceWrapper(symbols):
    DAYMINS = 60 * 24
    M = np.matrix(
        np.ones(DAYMINS), 
        np.array(range(DAYMINS))
    )

    p = 0.001 + 0.01

    limitsell = None
    
    def variance(data, state):
        assets = state['assets']

        for symbol in symbols:
            base, quote = symbol.value
            if assets[base] == 0 and assets[quote] == 0: continue


            candles1d = data.candles(symbol, DAYMINS)
            (b, a), r, _, _ = np.linalg.lstsq(M, candles1d.close)
            if 1 < a < 1.1 and p < r < 0.1:pass



    return variance