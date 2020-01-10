import re
import shutil
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from splinter import Browser
from splinter.driver.webdriver import BaseWebDriver

import models
from database import init_db
from db_models import Post
from log import logger
from settings import settings


def get_valid_filename(s):
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s).lower()


@logger.catch
def save_file(url, title):
    filename = get_valid_filename(title) + '.mp3'
    storage_dir = Path(settings.storage_path)
    storage_dir.mkdir(exist_ok=True)
    response = requests.get(url, stream=True)
    file_path = storage_dir.joinpath(filename).absolute()
    with open(file_path, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)

    return str(file_path)


@logger.catch
def init_browser():
    driver_settings = {
        'executable_path': settings.chromedriver_path,
        'headless': True
    }

    browser: BaseWebDriver = Browser('chrome', **driver_settings)
    browser.driver.maximize_window()
    browser.wait_time = 5
    browser.driver.set_page_load_timeout(15)
    return browser


class AbstractParser(ABC):
    name = ''

    def __init__(self, db=None):
        self.db = db or init_db()

    @abstractmethod
    @logger.catch
    def parse_post(self, url) -> models.Post:
        pass

    @logger.catch
    def save_post(self, model: models.Post):
        Post.create(**model.dict())

    @abstractmethod
    def urls(self) -> list:
        pass

    @logger.catch
    def run(self):
        logger.info(f'Run {self.__class__.__name__}')
        urls = self.urls()
        for url in urls:
            if not self.post_exists(url):
                try:
                    model = self.parse_post(url)
                    self.save_post(model)
                except Exception as e:
                    logger.exception(e)
                    continue

    @staticmethod
    def post_exists(url):
        exists = Post.select().where(Post.url == url).exists()
        if exists:
            logger.info(f'Post exists: {url}')
        else:
            logger.info(f'Found new post: {url}')
        return exists


class EnglishSoundParser(AbstractParser):
    name = 'spotlightenglish'

    def parse_post(self, url) -> models.Post:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        post = soup.find('article', class_='program')
        title = post.find('header').find('h2').getText()
        description = post.find('div', class_='program-description').getText()
        text = post.find(id='transcript').getText()
        mp3_url = post.find('a', attrs={'role': 'menuitem'}, href=True)['href']

        created_at = datetime.now(timezone.utc)
        path_to_file = save_file(mp3_url, title)

        return models.Post(
            url=url,
            name=self.name,
            title=title,
            description=description,
            text=text,
            created_at=created_at,
            file_path=path_to_file
        )

    def urls(self) -> list:
        response = requests.get('https://www.spotlightenglish.com/listen/')
        soup = BeautifulSoup(response.text, 'html.parser')

        post_urls = []
        posts = soup.find_all('h3', attrs={'class': 'media-heading'})
        for post in posts:
            href = post.find('a', href=True)['href']
            post_urls.append(urljoin('https://www.spotlightenglish.com', href))

        return post_urls


if __name__ == '__main__':
    EnglishSoundParser().run()
