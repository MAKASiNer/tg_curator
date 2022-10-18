from random import randbytes
from configparser import ConfigParser, DuplicateSectionError


TG_SECTOR = 'TELEGRAM'
DATABASE_SECTOR = 'DATABASE'
SERVICE = 'SERVICE'


_config = ConfigParser(allow_no_value=True)


# Возвращает опцию из сектора. Если опции или сектора нет, то вернет default
def safe_getopt(section, option, *, default=None):
    global _config
    if section not in _config:
        return default
    if option not in _config[section]:
        return default
    if _config[section][option] is None:
        return default
    return _config[section][option]


# Загружает конфиг из файла
def load_cfg():
    global _config
    _config.read('config.ini')


# Сохраняет конфиг в файл
def save_cfg():
    global _config

    try:
        _config.add_section(TG_SECTOR)
    except DuplicateSectionError:
        pass
    finally:
        _config[TG_SECTOR]['token'] = safe_getopt(TG_SECTOR, 'token')

    try:
        _config.add_section(DATABASE_SECTOR)
    except DuplicateSectionError:
        pass
    finally:
        _config.set(DATABASE_SECTOR, '; Available DBMS: sqlite, mysql, postgresql')
        _config[DATABASE_SECTOR]['dbms'] = safe_getopt(DATABASE_SECTOR, 'dbms', default='sqlite')
        _config[DATABASE_SECTOR]['name'] = safe_getopt(DATABASE_SECTOR, 'name', default='database.db')
        _config[DATABASE_SECTOR]['user'] = safe_getopt(DATABASE_SECTOR, 'user', default=None)
        _config[DATABASE_SECTOR]['password'] = safe_getopt(DATABASE_SECTOR, 'password')
        _config[DATABASE_SECTOR]['host'] = safe_getopt(DATABASE_SECTOR, 'host')
        _config[DATABASE_SECTOR]['port'] = safe_getopt(DATABASE_SECTOR, 'port')

    with open('config.ini', 'wt') as file:
        _config.write(file)


if __name__ == '__main__':
    load_cfg()
    save_cfg()
else:
    load_cfg()


TG_TOKEN = _config[TG_SECTOR]['token']

DB_DBMS = _config[DATABASE_SECTOR]['dbms']
DB_NAME = _config[DATABASE_SECTOR]['name']
DB_USER = _config[DATABASE_SECTOR]['user']
DB_PASSWORD = _config[DATABASE_SECTOR]['password']
DB_HOST = _config[DATABASE_SECTOR]['host']
DB_PORT = _config[DATABASE_SECTOR]['port']
