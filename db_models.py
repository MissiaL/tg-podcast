from uuid import uuid4

from peewee import CharField, DateTimeField, TextField, UUIDField, BooleanField

from database import BaseModel


class Post(BaseModel):
    id = UUIDField(default=uuid4)
    url = CharField(unique=True)
    name = CharField()
    title = CharField()
    description = TextField()
    text = TextField()
    created_at = DateTimeField()
    published_at = DateTimeField(null=True)
    file_path = CharField()
    file_deleted = BooleanField()

    class Meta:
        table_name = 'posts'
