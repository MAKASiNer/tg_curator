from datetime import datetime
import peewee as pw
import tgbot.data.config as config


if config.DB_DBMS == 'sqlite':
    db = pw.SqliteDatabase(config.DB_NAME)

elif config.DB_DBMS == 'mysql':
    db = pw.MySQLDatabase(
        database=config.DB_NAME,
        user=config.DB_USER,
        passwd=config.DB_PASSWORD,
        host=config.DB_HOST,
        port=config.DB_PORT
    )

elif config.DB_DBMS == 'postgresql':
    db = pw.PostgresqlDatabase(
        database=config.DB_NAME,
        user=config.DB_USER,
        passwd=config.DB_PASSWORD,
        host=config.DB_HOST,
        port=config.DB_PORT
    )

else:
    raise RuntimeError("Unavailable dbms '%s'" % config.DB_DBMS)


class BaseModel(pw.Model):
    class Meta:
        database = db


# -------------------------------------------------------------------------------------------------


class CallbacksData(BaseModel):
    '''
    Fields:
        json_str: str - json-строка с CallbackQuery.data
    '''
    json_str: str = pw.TextField(unique=True)


class Users(BaseModel):
    '''
    Fields:
        id             : int  - Соответсвует chat_id 
        username       : str  - Имя пользователя
        force_status   : bool - Права админимстратора
        hashed_password: str - хеш пароля
    '''
    username: str = pw.TextField()
    force_status: bool = pw.BooleanField(default=False)
    hashed_password: str = pw.TextField(null=True, unique=True)


class SuperuserSessions(BaseModel):
    '''
    Таблица сессий

    Fields:
        user         : User     - пользователь
        last_activity: datetime - Время последней отправки сообщения
    '''
    user: Users = pw.ForeignKeyField(Users, field='id')
    last_activity: datetime = pw.DateTimeField()


class Courses(BaseModel):
    '''
    Fields:
        title  : str  - Название курса
        testing: bool - Проводить ли тестирование в конце курса
        z_index: int  - Индекс для сортировки
    '''
    title: str = pw.TextField(unique=True)
    testing: bool = pw.BooleanField(default=True)
    z_index: int = pw.IntegerField(default=0)


class Pages(BaseModel):
    '''
    Fields:
        course   : int - Ссылка на Courses.id
        content     : str - Контент
        content_type: str - сейчас не используется
        z_index     : int - Индекс для сортировки
    '''
    course: int = pw.ForeignKeyField(Courses, to_field='id')
    content: str = pw.TextField()
    content_type: str = pw.TextField(default='str')
    z_index: int = pw.IntegerField(default=0)


class Questions(BaseModel):
    '''
    Fields:
        course   : Courses  - Ссылка на Courses
        text     : str      - Текст вопроса
        plural   : bool     - У вопроса несколько вариантов ответа? (только для various=True)
        various  : bool     - Пользователь выбирает ответ?
        z_index  : int      - Индекс для сортировки
    '''
    course: Courses = pw.ForeignKeyField(Courses, to_field='id')
    text: str = pw.TextField()
    plural: bool = pw.BooleanField()
    various: bool = pw.BooleanField()
    z_index: int = pw.IntegerField(default=0)


class Answers(BaseModel):
    '''
    Fields:
        question: Questions  - Cсылка на Questions
        text    : str        - Текст ответа
        right   : bool       - Это верный ответ?
        z_index : int        - Индекс для сортировки
    '''
    question: Questions = pw.ForeignKeyField(Questions, to_field='id')
    text: str = pw.TextField()
    right: bool = pw.BooleanField(default=False)
    z_index: int = pw.IntegerField(default=0)


# -------------------------------------------------------------------------------------------------


db.connect()
db.create_tables([CallbacksData, Users, SuperuserSessions, Courses, Pages, Questions, Answers], safe=True)
