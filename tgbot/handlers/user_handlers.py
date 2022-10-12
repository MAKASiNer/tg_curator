from telebot import formatting
from telebot.types import Message

from tgbot.loader import bot
from tgbot.data.models import Users
from tgbot.utils.bot_utils import get_actual_commands


@bot.message_handler(commands=['start'])
def start_handler(msg: Message):
    '''Приветствие'''
    Users.get_or_create(id=msg.from_user.id, username=msg.from_user.full_name)

    bot.send_message(chat_id=msg.chat.id,
                     text=(f'Привет, {msg.from_user.first_name}!\n'
                           f"Введи команду {formatting.hlink('/help', '/help')} чтобы вывести список всех команд.\n"))

    if Users.get_by_id(msg.from_user.id).force_status:
        bot.send_message(chat_id=msg.chat.id,
                         text='‼️Это сообщение видят только администраторы‼️')


@bot.message_handler(commands=['help'])
def help_handler(msg: Message):
    '''Список команд'''
    def docs(func):
        doc = func.__doc__
        return doc if doc else '...'

    lines = [f"{formatting.hlink('/' + k, '/' + k)} - {docs(v)}"
             for k, v in get_actual_commands(bot).items()]

    bot.send_message(chat_id=msg.chat.id,
                     text='\n'.join(lines))
