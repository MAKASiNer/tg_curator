from telebot import formatting
from telebot.types import Message, CallbackQuery

from tgbot.loader import bot, get_actual_commands
from tgbot.data.models import Users


# проверка на НЕ админа
def is_average(user_id: int):
    user: Users = Users.get_or_none(id=user_id)
    return not user or not user.force_status


# проверка сообщения от обычного пользователя
def from_average(msg):
    if isinstance(msg, (Message, CallbackQuery)):
        return is_average(msg.from_user.id)
    else:
        raise TypeError("msg must be 'Message' or 'CallbackQuery' class, not '%s'" % type(msg))


@bot.message_handler(commands=['start'], func=from_average)
def start_handler(msg: Message):
    '''Приветствие'''
    bot.send_message(chat_id=msg.chat.id,
                     text=(f'Привет, {msg.from_user.first_name}!\n'
                           f"Введи команду {formatting.hlink('/help', '/help')} чтобы вывести список всех команд.\n"))


@bot.message_handler(commands=['help'])
def help_handler(msg: Message):
    '''Список команд'''
    def docstr(cmd, func):
        return f"{formatting.hlink(f'/{cmd}', f'/{cmd}')} - {func.__doc__ if func.__doc__ else '...'}"

    bot.send_message(chat_id=msg.chat.id,
                     text='\n'.join(docstr(cmd, f) for cmd, f in get_actual_commands(bot).items()))