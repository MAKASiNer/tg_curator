from telebot import types

from tgbot.loader import bot
from tgbot.api.callbacks_api import *


PAGINATOR_OPEN_CMD = 'pgn_open'
PAGINATOR_BROWSE_PAGE_CMD = 'pgn_show'
PAGINATOR_CLOSE_CMD = 'pgn_close'


# тут в памяти хранятся стриницы пагинатора по ключу имени пагинатора
PAGES = dict()


def new_paginator(name: str, msg: types.Message, pages: list[str] = None):
    '''
    Трансформирует сообщени в пагинатор. Сообщение должно быть изменяемым

    Args:
        name:    str       - имя пагинатора, нужно для привязки страниц и фильтрации калбеков
        msg:  int          - Сообщение, которое будем насиловать в качестве дисплея
        pages:  list[str]  - список из страниц с текстом. Если указано, то изменит заменит страницы для ВСЕХ пагинаторов с таким же именем
    '''

    if pages:
        PAGES[name] = pages

    call = types.CallbackQuery(
        id=None,
        from_user=msg.from_user,
        data=make_callback_data(PAGINATOR_OPEN_CMD, {
                                'name': name, 'msg_id': msg.id}),
        chat_instance=str(types.Chat),
        message=msg
    )
    open_paginator(call)


@bot.callback_query_handler(func=lambda call: parse_callback_query(call)[0] == PAGINATOR_OPEN_CMD)
def open_paginator(call: types.CallbackQuery):
    '''
    Отображает список всех кнопок и кнопку "Закрыть"

    API:
        name   - имя пагинатора
        msg_id - id сообщения-дисплея
    '''
    data = parse_callback_query(call)[1]
    name, msg_id = data['name'], data['msg_id']

    markup = types.InlineKeyboardMarkup().add(
        *[
            types.InlineKeyboardButton(
                text=str(i + 1),
                callback_data=make_callback_data(
                    PAGINATOR_BROWSE_PAGE_CMD,
                    {'name': name, 'msg_id': msg_id, 'page': i}
                )
            ) for i, _ in enumerate(PAGES[name])
        ],

        types.InlineKeyboardButton(
            text='Закрыть',
            callback_data=make_callback_data(
                PAGINATOR_CLOSE_CMD,
                {'msg_id': msg_id}
            )
        ),

        row_width=1
    )

    bot.edit_message_reply_markup(
        call.message.chat.id, msg_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: parse_callback_query(call)[0] == PAGINATOR_BROWSE_PAGE_CMD)
def browse_page(call: types.CallbackQuery):
    '''
    Отображает конкретную страницу в пагинаторе

    API:
        name   - имя пагинатора
        msg_id - id сообщения-дисплея
        page   - индекс страницы (отсчет с 0)
    '''

    data = parse_callback_query(call)[1]
    name, msg_id, page = data['name'], data['msg_id'], data['page']
    size = len(PAGES[name])

    if page < 0 or page >= size:
        return

    l_btn = types.InlineKeyboardButton(
        text='<' if page > 0 else 'Х',
        callback_data=make_callback_data(
            PAGINATOR_BROWSE_PAGE_CMD,
            {'name': name, 'msg_id': msg_id, 'page': page - 1}
        )
    )

    md_btn = types.InlineKeyboardButton(
        text='...',
        callback_data=make_callback_data(
            PAGINATOR_OPEN_CMD, {'name': name, 'msg_id': msg_id}),
    )

    r_btn = types.InlineKeyboardButton(
        text='>' if page < size - 1 else 'Х',
        callback_data=make_callback_data(
            PAGINATOR_BROWSE_PAGE_CMD,
            {'name': name, 'msg_id': msg_id, 'page': page + 1}
        )
    )

    bot.edit_message_text(
        PAGES[name][page], call.message.chat.id, msg_id,
        reply_markup=types.InlineKeyboardMarkup().add(l_btn, r_btn, row_width=2).add(md_btn))


@bot.callback_query_handler(func=lambda call: parse_callback_query(call)[0] == PAGINATOR_CLOSE_CMD)
def close_paginator_callback(call: types.CallbackQuery):
    '''
    Закрыват стриницу с пагинатором.

    API:
        msg_id - id сообщения-дисплея
    '''
    msg_id = parse_callback_query(call)[1]['msg_id']
    bot.delete_message(call.message.chat.id, msg_id)
