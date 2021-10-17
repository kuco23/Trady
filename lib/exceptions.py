class OrderFillTimeot(Exception):
    pass

class InvalidPosition(Exception):
    def __init__(self, position):
        return f'trade position {position} not recognized'
