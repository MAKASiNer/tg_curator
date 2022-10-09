from telebot import TeleBot
from telebot.types import BotCommand


# словарь акруальных команд cmd:fucntion
def get_actual_commands(bot: TeleBot) -> dict:
    cmds = dict()
    for handler in bot.message_handlers:
        if 'commands' in handler['filters']:
            key = handler['filters']['commands'][0]
            cmds[key] = handler['function']
    return cmds


# генерирует описание команд на основе docstring и создает командное меню
def setup_commands_menu(bot: TeleBot):
    def docs(func):
        return func.__doc__ if func.__doc__ else '...'
    return bot.set_my_commands([
        BotCommand(k, docs(v)) for k, v in get_actual_commands(bot).items()
    ])
