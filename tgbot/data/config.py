from configparser import ConfigParser, DuplicateSectionError


_config = ConfigParser(allow_no_value=True)
_config.read('config.ini')


TG_SECTOR = 'TELEGRAM'
DATABASE_SECTOR = 'DATABASE'


# механизм создания файла конфига
if __name__ == '__main__':
    try:
        _config.add_section(TG_SECTOR)
        _config[TG_SECTOR]['token'] = None
    except DuplicateSectionError:
        pass

    try:
        _config.add_section(DATABASE_SECTOR)
        _config.set(DATABASE_SECTOR, '; Available DBMS: sqlite, mysql, postgresql')
        _config[DATABASE_SECTOR]['dbms'] = 'SqliteDatabase'
        _config[DATABASE_SECTOR]['name'] = 'database.db'
        _config[DATABASE_SECTOR]['user'] = ''
        _config[DATABASE_SECTOR]['password'] = ''
        _config[DATABASE_SECTOR]['host'] = ''
        _config[DATABASE_SECTOR]['port'] = ''

    except DuplicateSectionError:
        pass

    with open('config.ini', 'wt') as file:
        _config.write(file)


TG_TOKEN = _config[TG_SECTOR]['token']

DB_DBMS = _config[DATABASE_SECTOR]['dbms']
DB_NAME = _config[DATABASE_SECTOR]['name']
DB_USER = _config[DATABASE_SECTOR]['user']
DB_PASSWORD = _config[DATABASE_SECTOR]['password']
DB_HOST = _config[DATABASE_SECTOR]['host']
DB_PORT = _config[DATABASE_SECTOR]['port']
