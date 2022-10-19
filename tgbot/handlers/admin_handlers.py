from telebot import formatting, types

from tgbot.loader import bot
from tgbot.data.models import Users
from tgbot.utils.password_factory import secured_password
from tgbot.utils.callback_data_factory import *
from tgbot.filters.sessions_registrator import *


MAXIMUM_ATTEMPTS = 4
SIGNIN_TIMEOUT = 15


# проверка на админа
def is_superuser(user_id: int):
    user: Users = Users.get_or_none(id=user_id)
    return user and user.force_status


# проверка сообщения от админа
def from_superuser(msg):
    if isinstance(msg, (types.Message, types.CallbackQuery)):
        return is_superuser(msg.from_user.id)
    else:
        raise TypeError("msg must be 'Message' or 'CallbackQuery' class, not '%s'" % type(msg))


# запрашивает пароль и обновляет сессию
def signin_superuser(msg: types.Message):
    msg_id = bot.send_message(
        chat_id=msg.chat.id,
        text='Введи пароль'
    ).id

    def callback(m: types.Message, msg_id, attempt=1):
        session = get_superuser_session(m.from_user.id)
        bot.delete_message(m.chat.id, m.id)

        user = Users.get_by_id(m.from_user.id)

        # если превысили лимит попыток - лишаем прав администратора
        if attempt > MAXIMUM_ATTEMPTS:
            user.force_status = False
            user.save()
            bot.delete_message(m.chat.id, msg_id)
            return

        # пароль верный
        if secured_password(m.text) == user.hashed_password:
            bot.delete_message(m.chat.id, msg_id)
            update_superuser_session(session.id)
            return

        # пароль не верный
        else:
            at_left = MAXIMUM_ATTEMPTS - attempt
            if at_left == MAXIMUM_ATTEMPTS:
                text = 'Введи пароль'
            elif 1 < at_left < MAXIMUM_ATTEMPTS:
                text = 'Введи пароль (осталось попыток: %s)' % at_left
            elif at_left == 1:
                text = 'Введи верный пароль, иначе потеряешь права администратора'
            bot.edit_message_text(text, m.chat.id, msg_id)
            bot.register_next_step_handler(msg, callback, msg_id, attempt + 1)

    bot.register_next_step_handler(msg, callback, msg_id)


@bot.message_handler(commands=['start'], func=from_superuser)
def superuser_start_handler(msg: types.Message):
    '''Приветствие'''
    bot.send_message(chat_id=msg.chat.id,
                     text=(f'Привет, {msg.from_user.first_name}!\n'
                           f"Введи команду {formatting.hlink('/help', '/help')} чтобы вывести список всех команд.\n\n"
                           f'‼️Это сообщение видят только администраторы.\n'
                           f'‼️Команда {formatting.hlink("/admin", "/admin")} открывает админ-панель.'))


@bot.message_handler(regexp=r'/admin', func=from_superuser)
@register_superuser_session(timeout=SIGNIN_TIMEOUT, callback=signin_superuser)
def admin_handler(msg: types.Message):
    '''Выводит панель администратора'''
    markup = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton('Функция админа 1', callback_data=Api().make_callback_data()),
        types.InlineKeyboardButton('Функция админа 2', callback_data=Api().make_callback_data()),
        types.InlineKeyboardButton('Функция админа 3', callback_data=Api().make_callback_data())
    )
    bot.send_message(chat_id=msg.chat.id, text='Панель админа', reply_markup=markup)
