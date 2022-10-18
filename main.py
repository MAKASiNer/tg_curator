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


@cli.command(name='mkdb')
@click.option('--test', '-T', is_flag=True, default=False, help='Fill with test data')
def mkdb(test):
    '''Create database'''
    if test:
        import db_filler
        db_filler.main()
    import tgbot.data.models


@cli.command(name='superuser')
@click.option('--username', '-U', required=True, help='Full user name')
@click.option('--password', '-P', default=None, help='Set/change password and issue superuser status')
@click.option('--revoke', '-R', is_flag=True, help='Revoke superuser status')
def superuser(username, password, revoke):
    '''Give or take away superuser status'''
    from peewee import IntegrityError
    from tgbot.data.models import Users
    from tgbot.utils.password_factory import secured_password

    if not (user := Users.get_or_none(username=username)):
        click.echo('User not found')
        return
    
    if password:
        try:
            user.force_status = True
            user.hashed_password = secured_password(password)
            user.save()
        except IntegrityError:
            click.echo('This password is occupied')

    if revoke:
        user.force_status = False
        user.save()


if __name__ == '__main__':
    cli()
