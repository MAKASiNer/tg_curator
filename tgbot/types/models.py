import sqlite3
from dataclasses import dataclass, asdict, field, fields, Field


DB_PATH = 'database.db'

connection = sqlite3.Connection(DB_PATH, check_same_thread=False)
connection.execute('PRAGMA foreign_keys = ON;')


@dataclass
class Model:

    @classmethod
    @property
    def model_name(cls) -> str:
        return cls.__name__.lower()

    @classmethod
    @property
    def field_names(cls) -> list[str]:
        return [field.name for field in fields(cls)]

    @classmethod
    def SQLite_create_table_query(cls, exists_ok=False) -> str:
        '''
        Примечание:
            exist_ok - включает параметр IF NOT EXISTS в запрос
        '''
        cls_fields = [cls.render_SQLite_field(field) for field in fields(cls)]
        return f'''CREATE TABLE {"IF NOT EXISTS " if exists_ok else ""} {cls.model_name} ({', '.join(cls_fields)});'''

    @classmethod
    def SQLite_insert_query(cls, *, on_error: str = None, **kwargs) -> str:
        '''
        Примечание:
            on_error - или None, или 'ignore', или 'update'

            PRIMARY KEY игнорируются - не вызывают ошибок и не учитываются

            NOT NULL поля не могут быть инициализированы None значениями
        '''

        cls_fields = {field.name: field.default for field in fields(cls)}

        for key in kwargs:
            if key in cls_fields:
                cls_fields[key] = kwargs[key]
            else:
                raise ValueError(
                    f"Unexisted model field '{cls.model_name}.{key}'")

        for field in fields(cls):
            if field.metadata['primary_key']:
                cls_fields.pop(field.name)

            if field.metadata['not_null'] and cls_fields[field.name] is None:
                raise ValueError(
                    f"Field '{cls.model_name}.{field.name}' is setup as 'NOT NULL'")

        if on_error is None:
            insert = 'INSERT '
        elif on_error.lower() == 'ignore':
            insert = 'INSERT OR IGNORE '
        elif on_error.lower() == 'update':
            insert = 'INSERT OR REPLACE '
        else:
            insert = f'INSERT {on_error} '

        return (f'{insert} INTO {cls.model_name}'
                f'({",".join([ f""" "{key}" """ for key in cls_fields])}) '
                f'VALUES '
                f'({",".join([f""" "{value}" """ for key, value in cls_fields.items()])});')

    @classmethod
    def SQLite_select_query(cls, **kwargs) -> str:
        '''
        Механизм построени селекта прост. Существует 3 типа фильтров:

            Конкретные - проверяют строгое равенство
                Синтаксис:
                    "<имя поля>"
                Пример:
                    Model.SQLite_select_query(id=10)

            Исключающие - исключают из выборки значения, строго равные заданому
                Синтаксис:
                    "<имя поля>__exclude"
                Пример:
                    Model.SQLite_select_query(id__exclude=10)

                    Model.SQLite_select_query(title__exclude="text")

            Сравниваемые - включчают метод сравнения
                Синтаксис:
                    "<имя поля>__eq" - равно

                    "<имя поля>__ne" - не равно

                    "<имя поля>__lt" - меньше

                    "<имя поля>__le" - меньше или равно

                    "<имя поля>__gt" - больше,

                    "<имя поля>__ge" - больше или равно

                    "<имя поля>__bw" - между (ожидает коллекцию из 2 значений)

                    "<имя поля>__nb" - не между (ожидает коллекцию из 2 значений)

                    "<имя поля>__in" - в (ожидает коллекцию из 1 и более элементов)

                    "<имя поля>__ni" - не в (ожидает коллекцию из 1 и более элементов)

                Пример:
                    Model.SQLite_select_query(id__bw=(10, 100), num__le=50)

                    Model.SQLite_select_query(title__in=("aaa", "bbb", "ccc"))

        Примечание:
            Если НЕ УКАЗАН НИ ОДИН фильтр, то создастся запрос для выборки ВСЕХ данных
        '''

        columns = cls.field_names

        operators = list()

        for key in kwargs:
            # проверка аргумента
            cols = list(filter(lambda s: key.startswith(s), columns))
            if not cols:
                raise ValueError(f"Unexpected field '{key}'")
            
            col, method = key.split('__') + [None]

            if method in ('eq', None):
                operator = f'{col} = {kwargs[key]}'
            elif method in ('ne', 'exclude'):
                operator = f'{col} <> {kwargs[key]}'
            elif method == 'lt':
                operator = f'{col} < {kwargs[key]}'
            elif method == 'le':
                operator = f'{col} <= {kwargs[key]}'
            elif method == 'gt':
                operator = f'{col} > {kwargs[key]}'
            elif method == 'ge':
                operator = f'{col} >= {kwargs[key]}'
            elif method == 'bw':
                a, b, *_ = kwargs[key]
                operator = f'{col} BETWEEN {a} AND {b}'
            elif method == 'nb':
                a, b, *_ = kwargs[key]
                operator = f'{col} NOT BETWEEN {a} AND {b}'
            elif method == 'in':
                operator = f'{col} IN ({", ".join([f""" "{x}" """ for x in kwargs[key]])})'
            elif method == 'ni':
                operator = f'{col} NOT IN ({", ".join([f""" "{x}" """ for x in kwargs[key]])})'
            else:
                raise ValueError(f"Unexpected method '{method}'")

            operators.append(operator)

        if operators:
            return f'SELECT * FROM {cls.model_name} WHERE {" AND ".join(operators)}'
        return f'SELECT * FROM {cls.model_name}'

    @staticmethod
    def SQLite_field(type: str,
                     not_null: bool = False,
                     primary_key: bool = False,
                     autoincrement: bool = False,
                     unique: bool = False,
                     default=None,
                     foreign_key: tuple = None,  # пара (<таблица>, <столбец>)
                     on_delete: str = None,
                     on_update: str = None):

        return field(
            default=default,
            metadata={
                'type': type,
                'not_null': not_null,
                'primary_key': primary_key or autoincrement,
                'autoincrement': autoincrement,
                'unique': unique,
                'foreign_key': {
                    'table': foreign_key[0] if foreign_key and len(foreign_key) else None,
                    'column': foreign_key[1] if foreign_key and len(foreign_key) else None,
                    'on_delete': on_delete,
                    'on_update': on_update
                }
            }
        )

    @staticmethod
    def render_SQLite_field(field: Field):
        type = field.metadata.get('type', 'NULL')
        not_null = field.metadata.get('not_null', False)
        primary_key = field.metadata.get('primary_key', False)
        autoincrement = field.metadata.get('autoincrement', False)
        unique = field.metadata.get('unique', False)

        if (foreign_key := field.metadata.get('foreign_key', None)):
            foreign_table = foreign_key['table']
            foreign_column = foreign_key['column']
            on_delete = foreign_key['on_delete']
            on_update = foreign_key['on_update']
            foreign_key = foreign_column and foreign_table

        return (f'"{field.name}" '
                f'{type.upper()} '
                f'{"NOT NULL " if not_null else ""}'
                f'{"PRIMARY KEY " if primary_key or autoincrement else ""}'
                f'{"AUTOINCREMENT " if autoincrement else ""}'
                f'{"UNIQUE " if unique else ""}'
                f'{"""DEFAULT "{}" """.format(field.default) if field.default is not None else ""}'
                f'{f"""REFERENCES "{foreign_table}"("{foreign_column}") """ if foreign_table and foreign_column else ""}'
                f'{f"ON DELETE {on_delete.upper()} " if on_delete else ""}'
                f'{f"On UPDATE {on_update.upper()} " if on_update else ""}'
                )

    @classmethod
    def get(cls, **kwargs):
        '''
        Выполняет запрос Model.SQLite_select_query().

        Форматирутирует данные в список Model-объектов
        '''

        def init(*args):
            arg = iter(args)
            instance = cls()
            for field in cls.field_names:
                setattr(instance, field, next(arg))
            return instance

        return [init(*args) for args in connection.execute(cls.SQLite_select_query(**kwargs)).fetchall()]

    def save(self, on_error=None):
        '''
        Выплняет SQLite_insert_query для текущей записи.

        Примечание:
            В случае коллизий перезапишет запись. Это значит, что AUTOINCREMENT поля изменятся.
        '''
        connection.execute(self.__class__.SQLite_insert_query(
            on_error=on_error,
            **asdict(self)
        ))
        connection.commit()


@dataclass
class BaseTable(Model):
    id: int = Model.SQLite_field('integer', autoincrement=True)
    z_index: int = Model.SQLite_field('integer', not_null=True, default=0)


@dataclass
class Courses(BaseTable):
    '''
    Модель описывает курс.

    Поля:
        id - уникальный идентификатор курса

        title - название курса

        z_index - параметр для сортировки курсов (порядок, в котором будет отображен курс)

        has_test - должен ли курс проводить тестирование в конце

        shuffle_test - нужно ли перемешивать вопросы в случайном порядке
    '''
    title: str = Model.SQLite_field(
        type='text', not_null=True, unique=True)

    has_test: bool = Model.SQLite_field(
        type='boolean', not_null=True, default=False)

    shuffle_test: bool = Model.SQLite_field(
        type='boolean', not_null=True, default=False)


@dataclass
class Pages(BaseTable):
    '''
    Модель описывает одну страницу конкретного курса.

    Поля:
        id - уникальный идентификатор страницы

        z_index - параметр для сортировки страниц (порядок, в котором будут идти страницы)

        content - содержимое страницы, html документ для рендера телеграмом

        course_id - уникальный идентификатор курса, свзяывает страницу с конкретным курсом
    '''
    course_id: int = Model.SQLite_field(
        type='integer', foreign_key=('courses', 'id'), on_delete='set null')

    content: str = Model.SQLite_field(
        type='text', not_null=True)


@dataclass
class Tests(BaseTable):
    '''
    Модель описыват один тест конкретного курса

    Поля:
        id - уникальный идентификатор теста

        z_index - параметр для сортировки тестов (порядок, в котором будут идти тесты)

        course_id - уникальный идентификатор курса, свзяывает тест с конкретным курсом

        question - формулировка вопроса

        answer - содержит строковое представление правильного ответа


    Примечание:
        z_index будет иметь смысл только при shuffle=Falses
    '''
    course_id: int = Model.SQLite_field(
        type='integer', foreign_key=('courses', 'id'), on_delete='set null')

    question: str = Model.SQLite_field(
        type='text', not_null=True)

    answer: str = Model.SQLite_field(
        type='text', not_null=True)


if __name__ == '__main__':
    cur = sqlite3.Cursor(connection)

    # cur.execute(Courses.SQLite_select_query(id__bw=(1, 3)))
    # print(cur.fetchall())

    # cur.execute(Courses.SQLite_select_query(id__gt=1, id__lt=3))
    # print(cur.fetchall())

    # print(Courses.get(id__in=(0, 1, 2, 3)))
    # print(Courses.get(id__lt=3))
    # print(Courses.get(id__gt=1, id__lt=3))
    # exit()

    cur.execute(Courses.SQLite_create_table_query(exists_ok=True))
    cur.execute(Pages.SQLite_create_table_query(exists_ok=True))
    cur.execute(Tests.SQLite_create_table_query(exists_ok=True))

    # создаем 3 курса
    Courses(title='Курс 1').save(on_error='ignore')
    Courses(title='Курс 2').save(on_error='ignore')
    Courses(title='Курс 3').save(on_error='ignore')

    # создаем страницы
    Pages(
        course_id=1,
        z_index=10,
        content=('Lorem ipsum dolor sit amet, consectetur adipiscing elit, '
                 'sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. '
                 'Dui id ornare arcu odio ut sem nulla pharetra diam. Velit '
                 'scelerisque in dictum non consectetur a. Dignissim cras tincidunt '
                 'lobortis feugiat vivamus. Ornare arcu odio ut sem nulla pharetra '
                 'diam sit. Vestibulum lorem sed risus ultricies tristique nulla. '
                 'Porta nibh venenatis cras sed felis eget velit. Neque egestas '
                 'congue quisque egestas diam in arcu cursus euismod. Ullamcorper '
                 'dignissim cras tincidunt lobortis feugiat vivamus at augue eget. '
                 'Sapien pellentesque habitant morbi tristique senectus et netus et '
                 'malesuada. Tempor nec feugiat nisl pretium. Purus viverra accumsan '
                 'in nisl nisi scelerisque.')
    ).save(on_error='update')

    Pages(
        course_id=1,
        z_index=20,
        content=('Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed '
                 'do eiusmod tempor incididunt ut labore et dolore magna aliqua.')
    ).save(on_error='update')

    Pages(
        course_id=1,
        z_index=30,
        content=('Lorem ipsum dolor sit amet, consectetur adipiscing elit, '
                 'sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. '
                 'Dui id ornare arcu odio ut sem nulla pharetra diam. Velit '
                 'scelerisque in dictum non consectetur a. Dignissim cras tincidunt '
                 'lobortis feugiat vivamus. Ornare arcu odio ut sem nulla pharetra '
                 'diam sit. Vestibulum lorem sed risus ultricies tristique nulla.')
    ).save(on_error='update')

    Pages(
        course_id=2,
        content=('Lorem ipsum dolor sit amet, consectetur adipiscing elit, '
                 'sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. '
                 'Dui id ornare arcu odio ut sem nulla pharetra diam. Velit '
                 'scelerisque in dictum non consectetur a. Dignissim cras tincidunt '
                 'lobortis feugiat vivamus. Ornare arcu odio ut sem nulla pharetra '
                 'diam sit. Vestibulum lorem sed risus ultricies tristique nulla.')
    ).save(on_error='update')

    Pages(
        course_id=3,
        z_index=10,
        content=('Lorem ipsum dolor sit amet, consectetur adipiscing elit, '
                 'sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. '
                 'Dui id ornare arcu odio ut sem nulla pharetra diam.')
    ).save(on_error='update')

    Pages(
        course_id=3,
        z_index=20,
        content=('Lorem ipsum dolor sit amet, consectetur adipiscing elit, '
                 'sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. '
                 'Dui id ornare arcu odio ut sem nulla pharetra diam. Velit '
                 'scelerisque in dictum non consectetur a. Dignissim cras tincidunt '
                 'lobortis feugiat vivamus. Ornare arcu odio ut sem nulla pharetra '
                 'diam sit. Vestibulum lorem sed risus ultricies tristique nulla. ')
    ).save(on_error='update')

    Pages(
        course_id=3,
        z_index=30,
        content=('Lorem ipsum dolor sit amet, consectetur adipiscing elit, '
                 'sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. '
                 'Dui id ornare arcu odio ut sem nulla pharetra diam. Velit '
                 'scelerisque in dictum non consectetur a. Dignissim cras tincidunt '
                 'lobortis feugiat vivamus. Ornare arcu odio ut sem nulla pharetra '
                 'diam sit. Vestibulum lorem sed risus ultricies tristique nulla. '
                 'Porta nibh venenatis cras sed felis eget velit. Neque egestas '
                 'congue quisque egestas diam in arcu cursus euismod. Ullamcorper '
                 'dignissim cras tincidunt lobortis feugiat vivamus at augue eget.')
    ).save(on_error='update')

    Pages(
        course_id=3,
        z_index=40,
        content=('Lorem ipsum dolor sit amet, consectetur adipiscing elit,'
                 'sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. '
                 'Dui id ornare arcu odio ut sem nulla pharetra diam. Velit '
                 'scelerisque in dictum non consectetur a. Dignissim cras tincidunt '
                 'lobortis feugiat vivamus. Ornare arcu odio ut sem nulla pharetra '
                 'diam sit. Vestibulum lorem sed risus ultricies tristique nulla. '
                 'Porta nibh venenatis cras sed felis eget velit. Neque egestas '
                 'congue quisque egestas diam in arcu cursus euismod. Ullamcorper '
                 'dignissim cras tincidunt lobortis feugiat vivamus at augue eget. '
                 'Sapien pellentesque habitant morbi tristique senectus et netus et '
                 'malesuada. Tempor nec feugiat nisl pretium. Purus viverra accumsan '
                 'in nisl nisi scelerisque.')
    ).save(on_error='update')
