import os

from db_models import Post
from log import logger


def cleaner():
    logger.info('Start cleaner!')
    published_posts = Post.select().where(Post.published_at != None)
    for post in published_posts:
        os.remove(post.file_path)
        logger.info(f'File {post.file_path} was removed')
        Post.update(file_deleted=True).where(Post.id == post.id).execute()


if __name__ == '__main__':
    cleaner()
