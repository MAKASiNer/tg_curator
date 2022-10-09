from peewee import *
from tgbot.data.config import DB_PATH


db = SqliteDatabase(DB_PATH)


class BaseModel(Model):
    class Meta:
        database = db


class CallbacksData(BaseModel):
    json_str = TextField()


class Users(BaseModel):
    username = TextField()
    force_status = BooleanField(default=False)


class Courses(BaseModel):
    title = TextField(unique=True)
    testing = BooleanField(default=True)
    z_index = IntegerField(default=0)


class Pages(BaseModel):
    course_id = ForeignKeyField(Courses, to_field='id')
    content: str = TextField()
    content_type: str = TextField(default='str')
    z_index = IntegerField(default=0)


db.connect()
db.create_tables([CallbacksData, Users, Courses, Pages])
