from telebot import types
from random import randint

from tgbot.loader import bot
from tgbot.handlers import paginator
from tgbot.api.callbacks_api import *


COURSES_SHOW_ALL = 'crss_all'


def all_courses_ilkeyboard():

    courses = (
        'Что такое SQL?',
        'Основы таблиц',
        'Выборка данных',
        '...'
    )

    return types.InlineKeyboardMarkup().add(
        *[
            types.InlineKeyboardButton(
                text=title,
                callback_data=make_callback_data(
                    COURSES_SHOW_ALL, {'index': i}
                )
            ) for i, title in enumerate(courses)
        ],
        row_width=1
    )


@bot.callback_query_handler(func=lambda call: parse_callback_query(call)[0] == COURSES_SHOW_ALL)
def open_course(call: types.CallbackQuery):
    '''
    Открывает определенный курс

    API:
        index - номер курса (счет с 0)
    '''

    index = parse_callback_query(call)[1]['index']

    if index == 0:
        pages = ['lorem ipsum ' * randint(2, 20) for i in range(3)]
        paginator.new_paginator(
            name='course_1',
            msg=bot.send_message(call.message.chat.id, 'Выбери страницу курса#1'),
            pages=pages)

    elif index == 1:
        pages = ['lorem ipsum ' * randint(2, 20) for i in range(1)]
        paginator.new_paginator(
            name='course_1',
            msg=bot.send_message(call.message.chat.id, 'Выбери страницу курса#2'),
            pages=pages)

    elif index == 2:
        pages = ['lorem ipsum ' * randint(2, 20) for i in range(4)]
        paginator.new_paginator(
            name='course_1',
            msg=bot.send_message(call.message.chat.id, 'Выбери страницу курса#3'),
            pages=pages)