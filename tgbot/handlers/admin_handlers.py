from telebot import formatting, types

from tgbot.loader import bot
from tgbot.data.models import Users
from tgbot.filters.sessions_registrator import register_admin_session, get_session, update_session


# проверка на админа
def is_admin(user_id: int):
    user: Users = Users.get_or_none(id=user_id)
    return user and user.force_status


# проверка сообщения от админа
def from_admin(msg):
    if isinstance(msg, (types.Message, types.CallbackQuery)):
        return is_admin(msg.from_user.id)
    else:
        raise TypeError("msg must be 'Message' or 'CallbackQuery' class, not '%s'" % type(msg))


def signin_admin(msg: types.Message):
    bot.send_message(
        chat_id=msg.chat.id,
        text='Введи пароль'
    )

    def callback(m: types.Message):
        session = get_session(m.from_user.id)
        update_session(session.id)

    bot.register_next_step_handler(msg, callback)
    


@bot.message_handler(commands=['start'], func=from_admin)
def admin_start_handler(msg: types.Message):
    '''Приветствие'''
    bot.send_message(chat_id=msg.chat.id,
                     text=(f'Привет, {msg.from_user.first_name}!\n'
                           f"Введи команду {formatting.hlink('/help', '/help')} чтобы вывести список всех команд.\n\n"
                           f'‼️Это сообщение видят только администраторы.\n'
                           f'‼️Команда {formatting.hlink("/admin", "/admin")} открывает админ-панель.'))


@bot.message_handler(commands=['admin'], func=from_admin)
@register_admin_session(timeout=1800, callback=signin_admin)
def admin_handler(msg: types.Message):
    ...
