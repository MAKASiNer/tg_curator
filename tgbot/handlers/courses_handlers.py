import ttl_cache
from random import randint
from telebot import types, formatting
from dataclasses import dataclass, asdict

from tgbot.loader import bot
from tgbot.data.models import Courses, Pages
from tgbot.utils.callback_data_factory import *


@dataclass
class scpApi:
    '''
    Апи для показа страницы курса

    Fields:
        c_id - Courses.id

        p_id - Pages.id

        msg_id - идентификатор сообщения-дисплея

        end - показывать кнопку запуска тестирования?
    '''
    c_id: int
    p_id: int
    msg_id: int
    end: bool = False


@dataclass
class ccpApi:
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
            cmd = scpApi.__name__
            api = scpApi(c.id, get_pages(c.id)[0]._pk, msg_id)
            markup.add(types.InlineKeyboardButton(
                text=c.title,
                callback_data=make_callback_data(cmd, asdict(api))
            ))

    bot.edit_message_reply_markup(
        msg.chat.id, msg_id, reply_markup=markup)


def next_page_btn(api: scpApi):
    return types.InlineKeyboardButton(
        text='❯',
        callback_data=make_callback_data(
            cmd=scpApi.__name__,
            data=asdict(api)
        )
    )


def prev_page_btn(api: scpApi):
    return types.InlineKeyboardButton(
        text='❮',
        callback_data=make_callback_data(
            cmd=scpApi.__name__,
            data=asdict(api)
        )
    )


@bot.callback_query_handler(func=lambda q: parse_callback_query(q)[0] == scpApi.__name__)
def show_course_page_callback(query: types.CallbackQuery):
    api = scpApi(**parse_callback_query(query)[1])

    # номер страницы
    for i, p in enumerate(pages := get_pages(api.c_id)):
        if p.get_id() == api.p_id:
            p_i = i
            break

    # достигли конца курса ?
    api.end = True if p_i >= len(pages) - 1 else api.end

    markup = types.InlineKeyboardMarkup()

    # кнопки навигации
    if len(pages) > 1:
        if 0 < p_i < len(pages) - 1:
            markup.add(
                prev_page_btn(scpApi(api.c_id, pages[p_i-1].get_id(), api.msg_id, api.end)),
                next_page_btn(scpApi(api.c_id, pages[p_i+1].get_id(), api.msg_id, api.end)),
                row_width=2)
        elif p_i < len(pages) - 1:
            markup.add(
                next_page_btn(scpApi(api.c_id, pages[p_i+1].get_id(), api.msg_id, api.end)),
                row_width=1)
        elif p_i > 0:
            markup.add(
                prev_page_btn(scpApi(api.c_id, pages[p_i-1].get_id(), api.msg_id, api.end)),
                row_width=1)

    # если включено тестирование
    if api.end:

        from tgbot.handlers.testing_handlers import scqApi, get_questions

        # и для курса есть вопросы
        if (questions := get_questions(api.c_id)):
            markup.add(
                types.InlineKeyboardButton(
                    text='Начать тест',
                    callback_data=make_callback_data(
                        cmd=scqApi.__name__,
                        data=asdict(
                            scqApi(
                                c_id=api.c_id,
                                q_id=questions[0].id,
                                msg_id=api.msg_id,
                                score=0.0)))))

        markup.add(
            types.InlineKeyboardButton('Закрыть', callback_data=make_callback_data(ccpApi.__name__)),
            row_width=1
        )

    bot.edit_message_text(pages[p_i].content, query.message.chat.id, api.msg_id, reply_markup=markup)


@bot.callback_query_handler(func=lambda q: parse_callback_query(q)[0] == ccpApi.__name__)
def close_course_page_callback(query: types.CallbackQuery):
    bot.delete_message(query.message.chat.id, query.message.id)