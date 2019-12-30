from funcy import ignore
from pydantic import BaseSettings


@ignore(ImportError)
def try_to_load_dotenv() -> None:
    from dotenv import load_dotenv

    load_dotenv()


try_to_load_dotenv()


class Settings(BaseSettings):
    chromedriver_path: str = '.tools/chromedriver'
    storage_path: str = '.storage'

    db_name: str = 'app.sqlite'

    tg_proxy_enable: bool = False
    tg_proxy_username: str
    tg_proxy_password: str
    tg_proxy_url: str
    tg_bot_token: str
    tg_chat_id: str

    class Config:
        env_prefix = ''


settings = Settings()
