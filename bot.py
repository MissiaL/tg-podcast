from datetime import datetime, timezone

import telegram
from telegram.utils.request import Request

from db_models import Post
from log import logger
from settings import settings


def init_bot() -> telegram.Bot:
    bot_settings = {
        'token': settings.tg_bot_token
    }
    if settings.tg_proxy_enable:
        request = Request(
            proxy_url=settings.tg_proxy_url,
            urllib3_proxy_kwargs={
                'username': settings.tg_proxy_username,
                'password': settings.tg_proxy_password
            }
        )
        bot_settings.update({'request': request})

    bot = telegram.Bot(**bot_settings)
    return bot


def prepare_message(post: Post) -> str:
    message = f'*{post.title}*\n\n' \
              f'{post.url}\n\n' \
              f'#{post.name}'
    return message


@logger.catch
def publish():
    logger.info('Start to publish')
    bot = init_bot()

    unpublished_posts = Post.select().where(
        Post.published_at == None
    ).order_by(Post.created_at.desc()).limit(1)

    for post in unpublished_posts:
        logger.info(f'Publish {post.title}')
        msg = prepare_message(post)
        bot.send_message(
            chat_id=settings.tg_chat_id, text=msg, parse_mode='Markdown'
        )
        bot.send_audio(
            chat_id=settings.tg_chat_id,
            audio=open(post.file_path, 'rb'),
            timeout=300,
            title=post.title
        )
        Post.update(published_at=datetime.now(timezone.utc)).where(Post.id == post.id).execute()
        logger.info(f'Post {post.title} successfully published!')


if __name__ == '__main__':
    publish()
