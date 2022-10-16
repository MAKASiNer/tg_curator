import click

from tgbot.loader import bot
from tgbot.handlers import *


@click.group()
def cli():
    pass


@cli.command(name='run')
def run():
    '''Starts polling'''
    bot.infinity_polling()


if __name__ == '__main__':
    cli()
