import ttl_cache
from telebot import types
from dataclasses import dataclass, asdict

from tgbot.loader import bot
from tgbot.data.models import Courses, Pages
from tgbot.utils.callback_data_factory import *

from tgbot.handlers.testing_handlers import SCQapi, get_questions


@apiclass
class SCPapi(Api):
    '''
    Апи для показа страницы курса

    Fields:
        c_id  : int  - Courses.id
        p_id  : int  - Pages.id
        msg_id: int  - идентификатор сообщения-дисплея
        end   : bool - показывать кнопку запуска тестирования?
    '''
    c_id: int = 0
    p_id: int = 0
    msg_id: int = 0
    end: bool = False


@apiclass
class CCPapi(Api):
    '''Апи для закрытия сообщения со страницей'''


# возвращает отсортированные курсы
@ttl_cache(5.0)
def get_courses() -> list[Courses]:
    courses = Courses.filter()
    return sorted(courses, key=lambda x: x.z_index)


# возвращает отсортированные страницы для конкретного курса
@ttl_cache(5.0)
def get_pages(c_id: int) -> list[Pages]:
    pages = Pages.filter(course_id=c_id)
    return sorted(pages, key=lambda x: x.z_index)


@bot.message_handler(commands=['courses'])
def courses_handler(msg: types.Message):
    '''Список всех курсов'''

    msg_id = bot.send_message(
        chat_id=msg.chat.id,
        text='Нажми на курс чтобы открыть его',
    ).id

    markup = types.InlineKeyboardMarkup(row_width=1)
    for c in get_courses():
        if get_pages(c.id):

            data = SCPapi(c_id=c.id, p_id=get_pages(c.id)[0].id, msg_id=msg_id)

            markup.add(types.InlineKeyboardButton(
                text=c.title,
                callback_data=data.make_callback_data()
            ))

    bot.edit_message_reply_markup(
        msg.chat.id, msg_id, reply_markup=markup)


def next_page_btn(c_id, p_id, msg_id, end) -> types.InlineKeyboardButton:
    p_i = [p.id for p in get_pages(c_id)].index(p_id) + 1
    return types.InlineKeyboardButton(
        '❯', callback_data=SCPapi(c_id, get_pages(c_id)[p_i].id, msg_id, end).make_callback_data()
    )


def prev_page_btn(c_id, p_id, msg_id, end) -> types.InlineKeyboardButton:
    p_i = [p.id for p in get_pages(c_id)].index(p_id) - 1
    return types.InlineKeyboardButton(
        '❮', callback_data=SCPapi(c_id, get_pages(c_id)[p_i].id, msg_id, end).make_callback_data()
    )


@bot.callback_query_handler(func=SCPapi.filter)
def show_course_page_callback(query: types.CallbackQuery):
    api = SCPapi.parse_callback_query(query)

    # номер страницы
    for i, p in enumerate(pages := get_pages(api.c_id)):
        if p.get_id() == api.p_id:
            p_i = i
            break

    # достигли конца курса ?
    end = True if p_i >= len(pages) - 1 else api.end

    markup = types.InlineKeyboardMarkup()

    # кнопки навигации
    if len(pages) > 1:
        if 0 < p_i < len(pages) - 1:
            markup.add(
                prev_page_btn(api.c_id, api.p_id, api.msg_id, end),
                next_page_btn(api.c_id, api.p_id, api.msg_id, end),
                row_width=2
            )
        elif p_i < len(pages) - 1:
            markup.add(
                next_page_btn(api.c_id, api.p_id, api.msg_id, end))
        elif p_i > 0:
            markup.add(prev_page_btn(api.c_id, api.p_id, api.msg_id, end))

    # если включено тестирование
    if end:
        # и для курса есть вопросы
        if (questions := get_questions(api.c_id)):
            btn = types.InlineKeyboardButton(
                text='Начать тест',
                callback_data=SCQapi(c_id=api.c_id,
                                     q_id=questions[0].id,
                                     msg_id=api.msg_id,
                                     score=0.0).make_callback_data())
            markup.add(btn)

        btn = types.InlineKeyboardButton('Закрыть', callback_data=CCPapi().make_callback_data())
        markup.add(btn)

    bot.edit_message_text(pages[p_i].content, query.message.chat.id, api.msg_id, reply_markup=markup)


@ bot.callback_query_handler(func=CCPapi.filter)
def close_course_page_callback(query: types.CallbackQuery):
    bot.delete_message(query.message.chat.id, query.message.id)
