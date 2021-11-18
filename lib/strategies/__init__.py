from pathlib import Path

_cwd = Path().cwd() / 'lib' / 'strategies'

def _camelize(snakecase):
    classcase = snakecase.replace('_', ' ').title().replace(' ', '')
    camelcase = classcase[0].lower() + classcase[1:]
    return camelcase

def getStrategy(name, symbols):
    wrapper_name = _camelize(name + '_wrapper')
    wrapper = globals()[wrapper_name]
    return wrapper(symbols)

names = [
    path.stem for path in _cwd.iterdir()
    if path.is_dir() and path.stem != '__pycache__'
]

for name in names:
    wrappername = _camelize(name) + 'Wrapper'
    exec(f'from .{name}.{name} import {wrappername}')