from telebot import types
from random import randint

from tgbot.loader import bot
from tgbot.api.callbacks_api import *
from tgbot.types.models import Courses, Pages


COURSES_SHOW_ALL = 'crs@1'
COURSES_BROWSE_PAGE = 'crs@2'


# кэш страниц курса, ключ - id курса, значение - список id страниц
PAGES_CACHE: dict[str, list[int]] = dict()


def all_courses_ilkeyboard():
    # сортируем по z_index
    courses = sorted(Courses.get(), key=lambda x: x.z_index)
    # создаем markup с клавиатурой
    return types.InlineKeyboardMarkup().add(
        *[
            types.InlineKeyboardButton(
                text=course.title,
                callback_data=compile_callback_data(
                    COURSES_SHOW_ALL, {'c_id': course.id}
                )
            ) for course in courses
        ],
        row_width=1
    )


@bot.callback_query_handler(func=lambda call: parse_callback_query(call)[0] == COURSES_SHOW_ALL)
def open_course_callback(call: types.CallbackQuery):
    '''
    Открывает определенный курс

    API:
        c_id - идентификатор курса
    '''

    c_id = parse_callback_query(call)[1]['c_id']

    # вытаскиваем страницы конкретного курса и сортируем их по z_index
    pages = [page.id for page in sorted(
        Pages.get(course_id=c_id), key=lambda x: x.z_index)]

    # помещаем страницы в кэш
    PAGES_CACHE[c_id] = pages

    # создаем новый пагинатор с вытащенными и отсортированными страницами
    # paginator.new_paginator(
    #     name='1',
    #     msg=bot.send_message(call.message.chat.id, 'Выбери страницу'),
    #     pages=pages)

    browse_page_callback(types.CallbackQuery(
        id=None,
        from_user=None,
        data=compile_callback_data(COURSES_BROWSE_PAGE, {'c_id': c_id,
                                                      'p_id': pages[0],
                                                      'msg_id': call.message.id}),
        chat_instance=None,
        json_string=None,
        message=call.message
    ))


@bot.callback_query_handler(func=lambda call: parse_callback_query(call)[0] == COURSES_BROWSE_PAGE)
def browse_page_callback(call: types.CallbackQuery):
    '''
    Показывает страницу курса

    API:
        c_id - идентификатор курса
        p_id - идентификатор страница курса
        msg_id - идентификатор сообщения-дисплея
    '''
    data = parse_callback_query(call)[1]
    c_id = data['c_id']
    p_id = data['p_id']
    msg_id = data['msg_id']

    # если страниц нет в кеше, помещаем их туда
    if c_id not in PAGES_CACHE:
        PAGES_CACHE[c_id] = [page.content for page in sorted(
            Pages.get(course_id=c_id), key=lambda x: x.z_index)]

    pages_id = PAGES_CACHE[c_id]

    page_index = i if (i := pages_id.index(p_id)) != -1 else None

    def prev_btn():
        return types.InlineKeyboardButton(
            text='❮',
            callback_data=compile_callback_data(
                COURSES_BROWSE_PAGE,
                {'c_id': c_id,
                 'p_id': pages_id[page_index - 1],
                 'msg_id': msg_id}))

    def next_btn():
        return types.InlineKeyboardButton(
            text='❯',
            callback_data=compile_callback_data(
                COURSES_BROWSE_PAGE,
                {'c_id': c_id,
                 'p_id': pages_id[page_index + 1],
                 'msg_id': msg_id}))

    markup = types.InlineKeyboardMarkup()
    if 0 < page_index < len(pages_id) - 1:
        markup.add(prev_btn(), next_btn(), row_width=2)
    elif page_index <= 0 and len(pages_id) > 1:
        markup.add(next_btn(), row_width=1)
    elif page_index >= len(pages_id) - 1 and len(pages_id) > 1:
        markup.add(prev_btn(), row_width=1)

    bot.edit_message_text(
        text=Pages.get(id=p_id)[0].content,
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        reply_markup=markup
    )