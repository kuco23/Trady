from pathlib import Path
import configparser

path = Path().cwd() / Path('config.ini')

parser = configparser.ConfigParser()
parser.read(path, encoding='utf-8-sig')

def setVarName(section, key):
    return section.replace('-', '_').upper() + '_' + key.upper()

for section in parser.sections():
    keys = parser.options(section)
    globals().update(dict(zip(
        map(lambda key: setVarName(section, key), keys),
        map(lambda key: parser.get(section, key), keys)
    )))
