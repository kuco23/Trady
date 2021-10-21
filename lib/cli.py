import argparse
from datetime import datetime, timedelta

from .enums import Symbol
from . import strategies

class Argparser(argparse.ArgumentParser):

    class _SetStrategyAction(argparse.Action):
        def __call__(self, parser, namespace, values, ops=None):
            if len(values) > 2: raise argparse.ArgumentTypeError(
                'Too many arguments for strategy'
            )
            name, *sym = values
            symbol = Symbol.__members__.get(sym[0] if sym else None)
            strategy = getattr(strategies, name + 'Wrapper')
            setattr(namespace, self.dest, strategy(symbol))

    class _SetSymbolAction(argparse.Action):
        def __call__(self, parser, namespace, value, ops=None):
            symbol = Symbol.__members__.get(value)
            setattr(namespace, self.dest, symbol)
            
    class _SetStartDateAction(argparse.Action):
        def __call__(self, parser, namespace, values, ops=None):
            if not values: raise argparse.ArgumentTypeError(
                'Start date required'
            )
            setattr(namespace, self.dest, datetime(*values))

    class _SetEndDateAction(argparse.Action):
        def __call__(self, parser, namespace, values, ops=None):
            yesterday = datetime.now() - timedelta(days=1)
            ed = datetime(*values) if values else yesterday
            setattr(namespace, self.dest, ed)

    class _SetTimeIntervalAction(argparse.Action):
        def __call__(self, parser, namespace, value, ops=None):
            if value is not None and (value <= 0 or value % 1):
                raise argparse.ArgumentTypeError(
                    'Time interval must be a positive integer'
                )
            setattr(namespace, self.dest, timedelta(minutes=value or 1))

    def __init__(self, *args, **kwargs):
        self._ns = argparse.Namespace()
        super().__init__(*args, **kwargs)
                
    def add_argument_strategy(self):
        self.add_argument(
            'strategy', type=str, nargs='+',
            metavar='strategy',
            action=self._SetStrategyAction
        )

    def add_argument_symbol(self):
        self.add_argument(
            'symbol', type=str,
            metavar='symbol',
            action=self._SetSymbolAction
        )

    def add_argument_start_date(self):
        self.add_argument(
            '-sd', type=int, nargs=3,
            metavar='start date',
            action=self._SetStartDateAction
        )

    def add_argument_end_date(self):
        self.add_argument(
            '-ed', type=int, nargs=3,
             metavar='end date',
            action=self._SetEndDateAction
        )(self, self._ns, None)

    def add_argument_time_interval(self):
        self.add_argument(
            '-si', type=int,
            metavar='strategy time interval in minutes',
            action=self._SetTimeIntervalAction
        )(self, self._ns, None)

    # because transforming default values is a pain in the ass
    def parse_args(self):
        args = super().parse_args()
        for var, val in args._get_kwargs():
            if val is not None:
                setattr(self._ns, var, val)
        return self._ns
