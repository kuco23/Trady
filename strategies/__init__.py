from .bubble_find.bubble_find import bubbleFindWrapper
from .mean_revision_trend.mean_revision_trend import meanRevisionTrendWrapper
from .trend_spread.trend_spread import trendSpreadWrapper

'''
from importlib import import_module
from pathlib import Path

def camelize(snakecase):
    classcase = snakecase.replace('_', ' ').title().replace(' ', '')
    camelcase = classcase[0].lower() + classcase[1:]
    return camelcase

_cwd = Path().cwd() / 'strategies'

names = [
    path.stem for path in _cwd.iterdir()
    if path.is_dir() and path.stem != '__pycache__'
]

print(names)

for name in names:
    import_module(f'strategies.{name}.{name}', package='Trady')
    wrappername = camelize(name) + 'Wrapper'
    globals()[wrappername] = getattr(globals()[name], wrappername)

'''