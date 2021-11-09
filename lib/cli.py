import argparse
from datetime import datetime, timedelta

from .enums import Symbol
from . import strategies

class Argparser(argparse.ArgumentParser):

    class _SetStrategyAction(argparse.Action):
        def __call__(self, parser, namespace, values, ops=None):
            name, *syms = values
            clsname = name.replace('_', ' ').title().replace(' ', '')
            mthname = clsname[0].lower() + clsname[1:]
            symbols = list(map(Symbol.__members__.get, syms))
            strategy_obj = getattr(strategies, clsname)(symbols)
            strategy_meth = getattr(strategy_obj, mthname)
            setattr(namespace, self.dest, strategy_meth)

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
            setattr(namespace, self.dest, datetime(*values))

    class _SetTimeIntervalAction(argparse.Action):
        def __call__(self, parser, namespace, value, ops=None):
            if value <= 0 or value % 1: raise argparse.ArgumentTypeError(
                'Time interval must be a positive integer'
            )
            setattr(namespace, self.dest, timedelta(minutes=value))
                
    def add_argument_strategy(self):
        self.add_argument(
            'strategy', type=str, nargs='+',
            help='trading strategy',
            action=self._SetStrategyAction
        )

    def add_argument_symbol(self):
        self.add_argument(
            'symbol', type=str,
            help='trading symbol',
            action=self._SetSymbolAction
        )

    def add_argument_start_date(self):
        self.add_argument(
            '-sd', help='start date', type=int, nargs=3,
            metavar=('year', 'month', 'day'),
            action=self._SetStartDateAction
        )

    def add_argument_end_date(self):
        now = datetime.now()
        self.add_argument(
            '-ed', help='end date', type=int, nargs=3,
            metavar=('year', 'month', 'day'),
            default=[now.year, now.month, now.day],
            action=self._SetEndDateAction
        )
        
    def add_argument_time_interval(self):
        self.add_argument(
            '-ti', type=int, default=1, metavar='minutes',
            help='strategy time interval in minutes',
            action=self._SetTimeIntervalAction
        )

    # because transforming default values is a pain in the ass
    def parse_args(self):
        args = super().parse_args()
        for action in self._actions:
            if action.default == argparse.SUPPRESS: continue
            if action.default == getattr(args, action.dest):
                action(self, args, action.default)
        return args
