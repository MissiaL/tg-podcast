from peewee import Model, SqliteDatabase

from settings import settings

db = SqliteDatabase(settings.db_name)


def init_db():
    from db_models import Post
    db.bind([Post])
    db.connect(reuse_if_open=True)
    db.create_tables([Post])
    return db


class BaseModel(Model):
    class Meta:
        database = db
