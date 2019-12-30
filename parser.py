import re
import shutil
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path

import requests
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
        self.browser = init_browser()
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

    def __del__(self):
        self.browser.quit()


class EnglishSoundParser(AbstractParser):
    name = 'spotlightenglish'

    def parse_post(self, url) -> models.Post:
        self.browser.visit(url)
        title = self.browser.find_by_xpath("(//article[@class='program']//h2)[1]").text
        text = self.browser.find_by_xpath('//*[@id="transcript"]').text
        mp3_url = self.browser.find_by_xpath("(//a[@role='menuitem'])[1]")['href']
        created_at = datetime.now(timezone.utc)
        path_to_file = save_file(mp3_url, title)

        return models.Post(
            url=url,
            name=self.name,
            title=title,
            text=text,
            created_at=created_at,
            file_path=path_to_file
        )

    def urls(self) -> list:
        self.browser.visit('https://www.spotlightenglish.com/listen')
        urls = [e['href'] for e in self.browser.find_by_xpath("//aside[@class='media-body']//a")]
        return urls


if __name__ == '__main__':
    EnglishSoundParser().run()

