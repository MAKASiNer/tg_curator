from peewee import *
from enum import Enum
from tgbot.data.config import DB_PATH


db = SqliteDatabase(DB_PATH)


class BaseModel(Model):
    class Meta:
        database = db


class CallbacksData(BaseModel):
    '''
    Fields:
        json_str: str - json-строка с CallbackQuery.data
    '''
    json_str: str = TextField(unique=True)


class Users(BaseModel):
    '''
    Fields:
        username    : str  - Имя пользователя
        force_status: bool - Права админимстратора
    '''
    username: str = TextField()
    force_status: bool = BooleanField(default=False)


class Courses(BaseModel):
    '''
    Fields:
        title  : str  - Название курса
        testing: bool - Проводить ли тестирование в конце курса
        z_index: int  - Индекс для сортировки
    '''
    title: str = TextField(unique=True)
    testing: bool = BooleanField(default=True)
    z_index: int = IntegerField(default=0)


class Pages(BaseModel):
    '''
    Fields:
        course   : int - Ссылка на Courses.id
        content     : str - Контент
        content_type: str - сейчас не используется
        z_index     : int - Индекс для сортировки
    '''
    course: int = ForeignKeyField(Courses, to_field='id')
    content: str = TextField()
    content_type: str = TextField(default='str')
    z_index: int = IntegerField(default=0)


class Questions(BaseModel):
    '''
    Fields:
        course   : Courses  - Ссылка на Courses
        text     : str      - Текст вопроса
        plural   : bool     - У вопроса несколько вариантов ответа? (только для various=True)
        various  : bool     - Пользователь выбирает ответ?
        z_index  : int      - Индекс для сортировки
    '''
    course: Courses = ForeignKeyField(Courses, to_field='id')
    text: str = TextField()
    plural: bool = BooleanField()
    various: bool = BooleanField()
    z_index: int = IntegerField(default=0)


class Answers(BaseModel):
    '''
    Fields:
        question: Questions  - Cсылка на Questions
        text    : str        - Текст ответа
        right   : bool       - Это верный ответ?
        z_index : int        - Индекс для сортировки
    '''
    question: Questions = ForeignKeyField(Questions, to_field='id')
    text: str = TextField()
    right: bool = BooleanField(default=False)
    z_index: int = IntegerField(default=0)


db.connect()
db.create_tables([CallbacksData, Users, Courses, Pages, Questions, Answers])
