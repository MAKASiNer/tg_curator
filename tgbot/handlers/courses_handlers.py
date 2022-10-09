import ttl_cache
from telebot import types, formatting
from dataclasses import dataclass, asdict

from tgbot.loader import bot
from tgbot.models import Courses, Pages
from tgbot.utils.callback_data_factory import *


# @dataclass
# class OpenCourseApi:
#     c_id: int
#     msg_id: int


@dataclass
class ShowCoursePageApi:
    c_id: int
    p_id: int
    msg_id: int
    testing: bool = False


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
            cmd = ShowCoursePageApi.__name__
            api = ShowCoursePageApi(c.id, get_pages(c.id)[0]._pk, msg_id)
            markup.add(types.InlineKeyboardButton(
                text=c.title,
                callback_data=make_callback_data(cmd, asdict(api))
            ))

    bot.edit_message_reply_markup(
        msg.chat.id, msg_id, reply_markup=markup)


def next_page_btn(api: ShowCoursePageApi):
    return types.InlineKeyboardButton(
        text='❯',
        callback_data=make_callback_data(
            cmd=ShowCoursePageApi.__name__,
            data=asdict(api)
        )
    )


def prev_page_btn(api: ShowCoursePageApi):
    return types.InlineKeyboardButton(
        text='❮',
        callback_data=make_callback_data(
            cmd=ShowCoursePageApi.__name__,
            data=asdict(api)
        )
    )


@ bot.callback_query_handler(func=lambda q: parse_callback_query(q)[0] == ShowCoursePageApi.__name__)
def show_course_page_callback(query: types.CallbackQuery):
    api = ShowCoursePageApi(**parse_callback_query(query)[1])

    # номер страницы
    for i, p in enumerate(pages := get_pages(api.c_id)):
        if p.get_id() == api.p_id:
            p_i = i
            break

    # достигли конца курса
    api.testing = True if p_i >= len(pages) - 1 else api.testing

    markup = types.InlineKeyboardMarkup()

    if len(pages) > 1:
        if 0 < p_i < len(pages) - 1:
            markup.add(
                prev_page_btn(ShowCoursePageApi(api.c_id, pages[p_i-1].get_id(), api.msg_id, api.testing)),
                next_page_btn(ShowCoursePageApi(api.c_id, pages[p_i+1].get_id(), api.msg_id, api.testing)),
                row_width=2)
        elif p_i < len(pages) - 1:
            markup.add(
                next_page_btn(ShowCoursePageApi(api.c_id, pages[p_i+1].get_id(), api.msg_id, api.testing)),
                row_width=1)
        elif p_i > 0:
            markup.add(
                prev_page_btn(ShowCoursePageApi(api.c_id, pages[p_i-1].get_id(), api.msg_id, api.testing)),
                row_width=1)

    if api.testing:
        markup.add(types.InlineKeyboardButton(
            text='Пройти тест',
            callback_data=make_callback_data(None)
        ))

    bot.edit_message_text(Pages.get_by_id(api.p_id).content,
                          query.message.chat.id,
                          api.msg_id,
                          reply_markup=markup)
