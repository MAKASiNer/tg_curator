from pathlib import Path
from configparser import ConfigParser, DuplicateSectionError


_config = ConfigParser(allow_no_value=True)
_config.read('config.ini')


REQUIRED = 'REQUIRED'
OPTIONAL = 'OPTIONAL'


# механизм создания файла конфига
if __name__ == '__main__':
    try:
        _config.add_section(REQUIRED)
        _config[REQUIRED]['ttoken'] = None
    except DuplicateSectionError:
        pass

    try:
        _config.add_section(OPTIONAL)
    except DuplicateSectionError:
        pass

    with open('config.ini', 'wt') as file:
        _config.write(file)


# токен телеграм бота
TTOKEN = _config[REQUIRED]['ttoken']
    
# папка под базу данных
DB_PATH = Path(_config[OPTIONAL].get('db_dir', './')) / 'database.db'
