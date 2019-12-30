import factory
import pytest
from more_itertools import first
from peewee import SqliteDatabase

import models
from db_models import Post
from parser import AbstractParser


class PeeweeModelFactory(factory.Factory):
    """
    Based on PeeweeModelFactory from factory_boy-peewee,
    but _create doesn't calculate next pk,
    so it works only with pk's that unique by design (eg, UUIDs)
    """

    class Meta:
        abstract = True

    @classmethod
    def _create(cls, target_class, *args, **kwargs):
        model = target_class.create(**kwargs)
        return model


class PostFactory(PeeweeModelFactory):
    url = factory.Faker('image_url')
    title = factory.Faker('catch_phrase')
    text = factory.Faker('catch_phrase')
    published_at = factory.Faker('unix_time')
    file_path = factory.Faker('file_path')

    class Meta:
        model = Post


@pytest.fixture(autouse=True)
def db():
    test_db = SqliteDatabase(':memory:')
    test_db.bind([Post])

    test_db.connect()
    test_db.create_tables([Post])
    yield test_db
    test_db.drop_tables([Post])

    test_db.close()


def test_abstract_parser_test(db):
    size = 2
    fake_models = PostFactory.build_batch(size=size)

    class CustomParser(AbstractParser):
        def parse_post(self, url) -> models.Post:
            fake_model = first(m for m in fake_models if m.url == url)
            return models.Post(
                url=fake_model.url,
                name=self.name,
                title=fake_model.title,
                text=fake_model.text,
                file_path=fake_model.file_path
            )

        def urls(self) -> list:
            return [m.url for m in fake_models]

    CustomParser(db=db).run()
    assert Post.select().count() == size
