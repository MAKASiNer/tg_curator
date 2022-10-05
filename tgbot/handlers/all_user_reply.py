from telebot import types

from tgbot.loader import bot
from tgbot.handlers import courses


@bot.message_handler(commands=['start'])
def welcome_msg(msg: types.Message):
    '''вывести приветсвие'''
    bot.send_message(
        chat_id=msg.chat.id,
        text=(f'Привет, {msg.from_user.first_name}!\n'
              f'Введи команду "<code>/help</code>" чтобы вывести список всех команд.\n'),
        parse_mode='html'
    )


@bot.message_handler(commands=['courses'])
def courses_msg(msg: types.Message):
    '''список всех курсов'''
    bot.send_message(
        chat_id=msg.chat.id,
        text='Нажми на курс чтобы открыть его',
        reply_markup=courses.all_courses_ilkeyboard()
    )


@bot.message_handler(commands=['help'])
def help_msg(msg: types.Message):
    '''список всех команд'''

    cmds_and_descrs = [
        (
            handler['filters'].get('commands', [])[0],
            handler['function'].__doc__
        ) for handler in bot.message_handlers
    ]

    def key(x): return len(x[0])
    longest_cmd = key(max(cmds_and_descrs, key=key))

    lines = [
        f"<code>/{cmd.ljust(longest_cmd, ' ')}</code> - {descr}"
        for cmd, descr in sorted(cmds_and_descrs, key=lambda x: x[0])
    ]

    bot.send_message(
        chat_id=msg.chat.id,
        text='\n'.join(lines),
        parse_mode='html'
    )
