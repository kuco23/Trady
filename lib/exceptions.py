class OrderFillTimeot(Exception):
    pass

class InvalidPosition(Exception):
    def __init__(self, position):
        super().__init__(
            f'Trade position {position} not recognized.'
        )

class DatabaseCandleError(Exception):
    def __init__(self):
        return super().__init__(
            "This usually happens when a strategy requires "
            "candles that are not in the database."
        )
