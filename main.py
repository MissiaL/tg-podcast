import click


@click.group()
def cli():
    pass


@cli.command(help='Run parsers')
def collect():
    from parser import EnglishSoundParser
    EnglishSoundParser().run()


@cli.command(help='Clean storage files')
def clean():
    from tools import cleaner
    cleaner()


@cli.command(help='Publish all posts from db')
def publish():
    from bot import publish
    publish()


if __name__ == '__main__':
    cli()
