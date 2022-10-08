import ttl_cache
from telebot import types

from tgbot.loader import bot
from tgbot.types.models import Courses, Pages, Tests
from tgbot.api.callbacks_api import parse_callback_query, compile_callback_data


COURSES_SHOW_ALL = 'crs@1'
COURSES_BROWSE_PAGE = 'crs@2'
COURSES_START_TESTING = 'crs@3'


# возвращает список id страниц для конкретного курса
# страницы сортируются по z_index
@ttl_cache(1.0)
def get_pages_id(cource_id: int) -> list[int]:
    print('выхов get_pages_id')
    pages = Pages.get(course_id=cource_id)
    pages.sort(key=lambda x: x.z_index)
    return [p.id for p in pages]


# возвращает список id тестов для конкретного курса
# тесты сортируются по z_index
@ttl_cache(1.0)
def get_tests_id(cource_id: int) -> list[int]:
    tests = Tests.get(course_id=cource_id)
    tests.sort(key=lambda x: x.z_index)
    return [t.id for t in tests]


# инлайн кнопка для перехода к предыдущей странице курса
def prev_ilbtn(course_id, page_index, message_id, finished):
    return types.InlineKeyboardButton(
        text='❮',
        callback_data=compile_callback_data(
            COURSES_BROWSE_PAGE,
            {'c_id': course_id,
                'p_id': get_pages_id(course_id)[page_index - 1],
                'msg_id': message_id,
                'fshd': finished}
        )
    )


# инлайн кнопка для перехода к следующей странице курса
def next_ilbtn(course_id, page_index, message_id, finished):
    return types.InlineKeyboardButton(
        text='❯',
        callback_data=compile_callback_data(
            COURSES_BROWSE_PAGE,
            {'c_id': course_id,
                'p_id': get_pages_id(course_id)[page_index + 1],
                'msg_id': message_id,
                'fshd': finished}
        )
    )


# инлайн кнопка для начала тестирования
def testing_ilbtn(course_id, message_id):
    return types.InlineKeyboardButton(
        text='Пройти тест',
        callback_data=compile_callback_data(
            COURSES_START_TESTING,
            {'c_id': course_id,
                't_id': get_tests_id(course_id)[0],
                'msg_id':  message_id}
        )
    )


# инлайн кнопки со списком всех кнопок
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


@bot.callback_query_handler(func=lambda c: parse_callback_query(c)[0] == COURSES_SHOW_ALL)
def open_course_callback(call: types.CallbackQuery):
    '''
    Открывает определенный курс

    API:
        c_id - идентификатор курса
    '''

    c_id = parse_callback_query(call)[1]['c_id']
    p_id = get_pages_id(c_id)[0]

    browse_page_callback(types.CallbackQuery(
        id=None,
        from_user=None,
        data=compile_callback_data(COURSES_BROWSE_PAGE, {'c_id': c_id,
                                                         'p_id': p_id,
                                                         'msg_id': call.message.id,
                                                         'fshd': 0}),
        chat_instance=None,
        json_string=None,
        message=call.message
    ))


@bot.callback_query_handler(func=lambda c: parse_callback_query(c)[0] == COURSES_BROWSE_PAGE)
def browse_page_callback(call: types.CallbackQuery):
    '''
    Показывает страницу курса

    API:
        c_id - идентификатор курса
        p_id - идентификатор страница курса
        msg_id - идентификатор сообщения-дисплея
        fshd - был ли достигнут конец
    '''
    data = parse_callback_query(call)[1]
    course = Courses.get_one(id=data['c_id'])
    page = Pages.get_one(id=data['p_id'])
    msg_id = data['msg_id']

    pages_id = get_pages_id(course.id)
    page_index = pages_id.index(page.id)

    # достигли ли конца курса ?
    fshd = data['fshd'] if page_index < len(pages_id) - 1 else 1
    
    markup = types.InlineKeyboardMarkup()

    # первая страница
    if 0 < page_index < len(pages_id) - 1:
        markup.add(
            prev_ilbtn(course.id, page_index, msg_id, fshd),
            next_ilbtn(course.id, page_index, msg_id, fshd),
            row_width=2
        )
    # средние страницы
    elif page_index <= 0 and len(pages_id) > 1:
        markup.add(
            next_ilbtn(course.id, page_index, msg_id, fshd),
            row_width=1
        )
    # последняя страницы
    elif page_index >= len(pages_id) - 1 and len(pages_id) > 1:
        markup.add(
            prev_ilbtn(course.id, page_index, msg_id, fshd),
            row_width=1
        )
    # курс одностраничный
    else:
        pass

    # кнопка тестирования появляется только если
    # - дослигли конца курса
    # - у курса включенно тестирование
    # - в базе данных есть хотя бы один тест
    if fshd and course.testing_on and get_tests_id(course.id):
        markup.add(
            testing_ilbtn(course.id, msg_id),
            row_width=1
        )

    bot.edit_message_text(
        text=page.content,
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda c: parse_callback_query(c)[0] == COURSES_START_TESTING)
def start_testing_callback(call: types.CallbackQuery):
    '''
    Запускает тестирование по курсу
    '''
    data = parse_callback_query(call)[1]
    print(data)
