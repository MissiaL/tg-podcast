import click


@click.group()
def cli():
    pass


@cli.command(help='Run parsers')
def pull():
    from parser import EnglishSoundParser
    EnglishSoundParser().run()


@cli.command(help='Clean storage files')
def clean():
    from tools import cleaner
    cleaner()


@cli.command(help='Publish all posts from db')
def push():
    from bot import publish
    publish()


if __name__ == '__main__':
    cli()
