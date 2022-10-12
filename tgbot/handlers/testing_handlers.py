import ttl_cache
from telebot import formatting
from telebot.types import *
from dataclasses import dataclass, asdict

from tgbot.loader import bot
from tgbot.data.models import *
from tgbot.utils.general import shuffle_by_z_index
from tgbot.utils.callback_data_factory import *


CHECKBOX_ON = '✅'
CHECKBOX_OFF = '❌'

COMMIT_ANSWER = 'Далее'


@apiclass
class SCQapi(Api):
    '''
    Апи для вывода вопроса курса

    Fields:
        c_id  : int   - Courses.id
        q_id  : int   - Questions.id
        msg_id: int   - идентификатор сообщения-дисплея
        score : float - количество баллов
    '''
    c_id: int = 0
    q_id: int = 0
    msg_id: int = 0
    score: float = 0


@ apiclass
class NQPapi(Api):
    '''
    Апи для обработки not plural вопросов

    Fields:
        a_id  : int - Answers.id
        msg_id: int - идентификатор сообщения-дисплея
        score : int - счет
    '''
    a_id: int = 0
    msg_id: int = 0
    score: float = 0


@apiclass
class PEQapi(Api):
    '''
    Апи для обработки plural вопросов

    Fields:
        a_id  : int   - Answers.id
        btn_i : int   - индекс кнопки внутри Markup
        msg_id: int   - идентификатор сообщения-дисплея
        score : float - счет
    '''
    a_id: int = 0
    btn_i: int = 0
    msg_id: int = 0
    score: float = 0


# возвращает остортированный список тестовых вопросов для конкретного курса
@ttl_cache(5.0)
def get_questions(c_id: int) -> list[Questions]:
    questions = sorted(Questions.filter(course_id=c_id), key=lambda x: x.z_index)
    shuffle_by_z_index(questions)
    return questions


# возвращает отсортированный список ответов для конкретного вопроса
@ttl_cache(5.0)
def get_answers(q_id: int) -> list[Answers]:
    answers = sorted(Answers.filter(question_id=q_id), key=lambda x: x.z_index)
    shuffle_by_z_index(answers)
    return answers


# возвращает id следующего вопроса и None если следующего нет
def next_q_id(q_id: int):
    try:
        quest = Questions.get_by_id(q_id)
        q_i = [q.id for q in get_questions(quest.course.id)].index(q_id)
        id: int = get_questions(quest.course.id)[q_i + 1].get_id()
        return id
    except IndexError:
        return None


@bot.message_handler(commands=['start_testing'])
def start_testing_handler(msg: Message):
    '''Запускает тестирование по курсу'''
    arg = msg.text.lstrip('/start_testing').strip()

    # справшиваем курс если он не указан аргументом команды
    if not arg:
        bot.send_message(msg.chat.id, 'Введи название курса, тестирование по которому хочешь пройти')
        return bot.register_next_step_handler(msg, start_testing_handler)

    # проверяем курс на существование
    if not (course := Courses.get_or_none(title=arg)):
        return bot.send_message(
            chat_id=msg.chat.id,
            text=(f'Курс под названием {formatting.hitalic(arg)} не найден. '
                  f'Введи команду {formatting.hlink("/courses", "/courses")} чтобы вывести список всех курсов'))

    # проверяем есть/разрешено тетсирование у курса
    if not course.testing or not (questions := get_questions(course.id)):
        return bot.send_message(
            chat_id=msg.chat.id,
            text=f'Для курса под названием {formatting.hitalic(arg)} не предусмотрено тестирования.')

    # запускаем первый квест
    show_course_quest_callback(
        SCQapi(c_id=course.id,
               q_id=questions[0].id,
               msg_id=bot.send_message(msg.chat.id, '...').id,
               score=0.0).make_callback_query(msg)
    )


# создает клавиатуру под вопрос
def make_testing_markup(q_id: int, _msg_id: int, score: float):
    quest: Questions = Questions.get_by_id(q_id)

    if not quest.various:
        return

    # обработка вопросов с несколькими ответами
    if quest.plural:
        # query калбек
        def callback(q: CallbackQuery):
            api = PEQapi.parse_callback_query(q)
            # посчитываем баллы и переходим к следующему вопросу если нажали на COMMIT_ANSWER кнопку
            if not api.a_id:
                # кол-во ответов (a) и кол-во правильный из них (b)
                a, b = 0, 0
                for btn, *_ in q.message.reply_markup.keyboard:
                    # пропускаем если это COMMIT_ANSWER
                    if not (a_id := PEQapi.parse_callback_data(btn.callback_data).a_id):
                        continue
                    # увелчиваем колв-во ответов и проверяем верный ли ответ
                    answer: Answers = Answers.get_by_id(a_id)
                    b += 1 if (CHECKBOX_ON in btn.text) == (answer.right) else - 1
                    a += 1

                # запускаем следующий вопрос
                show_course_quest_callback(
                    SCQapi(c_id=answer.question.course.id,
                           q_id=next_q_id(answer.question.id),
                           msg_id=api.msg_id,
                           score=api.score + max(0, b/a)).make_callback_query(q.message)
                )

            # инвертируем CHECKBOX_OFF и CHECKBOX_ON если нажали на вариант ответа
            else:
                text = q.message.reply_markup.keyboard[api.btn_i][0].text
                if CHECKBOX_OFF in text:
                    q.message.reply_markup.keyboard[api.btn_i][0].text = text.replace(CHECKBOX_OFF, CHECKBOX_ON, 1)
                elif CHECKBOX_ON in text:
                    q.message.reply_markup.keyboard[api.btn_i][0].text = text.replace(CHECKBOX_ON, CHECKBOX_OFF, 1)
                # применяем изменения
                bot.edit_message_reply_markup(q.message.chat.id, api.msg_id, reply_markup=q.message.reply_markup)

        # регистрируем калбек
        bot.register_callback_query_handler(callback, PEQapi.filter)

        # создаем клавиатуру под этот калбек
        btns = [
            InlineKeyboardButton(
                text=f'{CHECKBOX_OFF} {a.text}',
                callback_data=PEQapi(a_id=a.id, btn_i=i, msg_id=_msg_id, score=score).make_callback_data()
            ) for i, a in enumerate(get_answers(q_id))
        ] + [
            InlineKeyboardButton(
                text=COMMIT_ANSWER,
                callback_data=PEQapi(a_id=None, btn_i=None, msg_id=_msg_id, score=score).make_callback_data()
            )
        ]
        return InlineKeyboardMarkup().add(*btns, row_width=1)

    # обработка вопросов с одним ответом
    else:
        # query калбек
        def callback(q: CallbackQuery):
            api = NQPapi.parse_callback_query(q)
            answer: Answers = Answers.get_by_id(api.a_id)
            show_course_quest_callback(
                SCQapi(c_id=answer.question.course.id,
                       q_id=next_q_id(answer.question.id),
                       msg_id=api.msg_id,
                       score=api.score + (1.0 if answer.right else 0)).make_callback_query(q.message)
            )
        # регистрируем калбек
        bot.register_callback_query_handler(callback, NQPapi.filter)
        # создаем клавиатуру под этот калбек
        btns = [
            InlineKeyboardButton(
                text=a.text,
                callback_data=NQPapi(a_id=a.id, msg_id=_msg_id, score=score).make_callback_data()
            ) for a in get_answers(q_id)
        ]
        return InlineKeyboardMarkup().add(*btns, row_width=1)


# возвращает подсказку для определенного типа вопросов
def make_testing_tooltip(quest: Questions):
    if quest.various:
        if quest.plural:
            return f'Выбери несколько вариантов ответов и нажми на "{COMMIT_ANSWER}"'
        else:
            return f'Выбери один вариант ответа'

    return f'Введи ответ в чат'


# показывает конкретный вопрос курса
@ bot.callback_query_handler(func=SCQapi.filter)
def show_course_quest_callback(query: CallbackQuery):
    api = SCQapi.parse_callback_query(query)

    questions = get_questions(api.c_id)

    # подводим итоги если больше нет вопросов
    if api.q_id not in (arr := [q.id for q in questions]):
        return bot.edit_message_text(
            text=f'Ты набрал {formatting.hbold(f"{api.score:.2f}")} из {formatting.hbold(f"{len(questions):.2f}")} баллов!',
            chat_id=query.message.chat.id,
            message_id=api.msg_id,
            reply_markup=InlineKeyboardMarkup()
        )

    q_i = arr.index(api.q_id)
    quest = questions[q_i]

    # создаем next_step_handler если ответ с воодом из чата
    if not quest.various:
        def callback(m: Message, c_id, q_id, msg_id,  score):
            # зачисляем баллы
            if m.text.lower() in [a.text.lower() for a in get_answers(q_id)]:
                score += 1.0
            # удаляем сообщение пользователя
            bot.delete_message(m.chat.id, m.id)
            show_course_quest_callback(
                SCQapi(c_id=c_id, q_id=next_q_id(q_id), msg_id=msg_id, score=score).make_callback_query(m)
            )

        bot.register_next_step_handler(query.message, callback, api.c_id, api.q_id, api.msg_id, api.score)
        markup = InlineKeyboardMarkup()

    # создаем InlineMarkup если ответ с выбором варианта\вариантов
    else:
        markup = make_testing_markup(quest.id, api.msg_id, api.score)

    bot.edit_message_text(
        text=formatting.hitalic(f'Вопрос №{q_i + 1}. {make_testing_tooltip(quest)}:\n\n') + quest.text,
        chat_id=query.message.chat.id,
        message_id=api.msg_id,
        reply_markup=markup
    )
