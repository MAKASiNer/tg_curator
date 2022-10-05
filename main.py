from tgbot.loader import bot
from tgbot.handlers import all_user_reply


bot.infinity_polling()

# import json
# import telebot
# from telebot import types


# TOKEN = '5791974173:AAGbOUil-ACSXKgrbwjVqyHNvBCa-rI6jHw'
# bot = telebot.TeleBot(TOKEN)


# BROWSE_COURSE = 'brws_crs'
# BROWSE_ALL_COURSES = 'brws_all_crss'
# CLOSE_CURSES_BROWSER = 'cls_crss_brws'


# def make_callback_data(handler: str, data=None):
#     return json.dumps([handler, data])


# def parse_callback_data(s: str):
#     handler: str
#     handler, data = json.loads(s)
#     return handler, data





# def welcome_reply(msg: types.Message):

#     if msg.text == 'Курсы':
#         open_courses_browser(msg)

#     elif msg.text == 'SQL интерпретатор':
#         ...

#     elif msg.text == 'Подробнее о боте':
#         ...

#     else:
#         bot.send_message(msg.chat.id, 'Я не знаю такой команды')
#         bot.register_next_step_handler(msg, welcome_reply)


# @bot.message_handler(commands=['courses'])
# def open_courses_browser(msg: types.Message):

#     tmp_msg = bot.send_message(
#         msg.chat.id, '...', reply_markup=types.ReplyKeyboardRemove())
#     bot.delete_message(tmp_msg.chat.id,  tmp_msg.id)

#     # отправляем сообщение, которое будем насиловать в дальнейшем
#     target_msg = bot.send_message(
#         chat_id=msg.chat.id,
#         text='Список всех курсов:',
#     )

#     # создаем фиктивное сообщение о нажатии inline
#     call = types.CallbackQuery(
#         id=msg.id,
#         from_user=msg.from_user,
#         data=make_callback_data(BROWSE_ALL_COURSES, {'msg_id': target_msg.id}),
#         chat_instance=msg.chat.id,
#         message=msg
#     )

#     # порождаем callback
#     browser_all_courses_callback(call)


# @bot.callback_query_handler(func=lambda call: parse_callback_data(call.data)[0] == BROWSE_ALL_COURSES)
# def browser_all_courses_callback(call: types.CallbackQuery):
#     # парсим данные из call
#     data = parse_callback_data(call.data)[1]
#     msg_id = data['msg_id']

#     courses = ('Что такое SQL?', 'Основы таблиц', 'Выборка данных', '...')

#     # создаем список курсов
#     markup = types.InlineKeyboardMarkup().add(
#         *[
#             types.InlineKeyboardButton(
#                 text=title,
#                 # в данные помещаем номер курсов, их количество и id того самого сообщения из open_courses_browser
#                 callback_data=make_callback_data(BROWSE_COURSE, {
#                     'i': i,
#                     'size': len(courses),
#                     'msg_id': msg_id
#                 })
#             ) for i, title in enumerate(courses)
#         ],

#         types.InlineKeyboardButton(
#             text='Закрыть',
#             callback_data=make_callback_data(CLOSE_CURSES_BROWSER, {'msg_id': msg_id})),

#         row_width=1
#     )

#     # наилуем то самое сообщение из open_courses_browser
#     bot.edit_message_reply_markup(
#         chat_id=call.message.chat.id,
#         message_id=msg_id,
#         reply_markup=markup
#     )


# @bot.callback_query_handler(func=lambda call: parse_callback_data(call.data)[0] == BROWSE_COURSE)
# def browse_course_callback(call: types.CallbackQuery):
#     # парсим данные из call
#     data = parse_callback_data(call.data)[1]
#     i, size, msg_id = data['i'], data['size'], data['msg_id']

#     if i < 0 or i >= size:
#         return

#     # создаем кнопку "предыдущий курс"
#     prev_btn = types.InlineKeyboardButton(
#         text='<--' if i > 0 else 'X',
#         callback_data=make_callback_data(BROWSE_COURSE, {
#             'i': i - 1,
#             'size': size,
#             'msg_id': msg_id
#         })
#     )

#     # создаем кнопку "список курсов"
#     midl_btn = types.InlineKeyboardButton(
#         text='...',
#         callback_data=make_callback_data(
#             BROWSE_ALL_COURSES, {'msg_id': msg_id})
#     )

#     # создаем кнопку "следующий курс"
#     next_btn = types.InlineKeyboardButton(
#         text='-->' if i < size - 1 else 'X',
#         callback_data=make_callback_data(BROWSE_COURSE, {
#             'i': i + 1,
#             'size': size,
#             'msg_id': msg_id
#         })
#     )

#     # наилуем то самое сообщение из open_courses_browser
#     bot.edit_message_text(
#         text=str(i).rjust(21, '.').ljust(41, '.'),
#         chat_id=call.message.chat.id,
#         message_id=msg_id,
#         reply_markup=types.InlineKeyboardMarkup().add(
#             prev_btn, midl_btn, next_btn,
#             row_width=3)
#     )


# @bot.callback_query_handler(func=lambda call: parse_callback_data(call.data)[0] == CLOSE_CURSES_BROWSER)
# def close_courses_browser_callback(call: types.CallbackQuery):
#     # парсим данные из call
#     data = parse_callback_data(call.data)[1]
#     msg_id = data['msg_id']

#     # удаляем сообщение
#     bot.delete_message(call.message.chat.id, msg_id)


# bot.infinity_polling()
