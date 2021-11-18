class OrderFillTimeout(Exception):
    pass

class InvalidPosition(Exception):
    def __init__(self, position):
        super().__init__(
            f'Trade position {position} not recognized.'
        )

class DatabaseCandleError(Exception):
    def __init__(self, symbol):
        super().__init__(
            f"Error in the database from {symbol.name} table."
            "This usually happens when a strategy requires "
            "candles that are not in the database."
        )

class InsufficientData(Exception):
    def __init__(self, symbol, reqsd, reqed):
        super().__init__(
            f"You do not have candle data for {symbol.name} "
            f"for the time during {reqsd} and {reqed}! "
            f"Check info.py {symbol.name} for the information "
            "about the candles in the database"
        )
