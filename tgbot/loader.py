from telebot import TeleBot
from telebot.types import BotCommand

from tgbot.data.config import TG_TOKEN


bot = TeleBot(TG_TOKEN, parse_mode='html')


# словарь акруальных команд
def get_actual_commands(bt: TeleBot = bot) -> dict[str, ]:
    cmds = dict()
    for handler in bt.message_handlers:
        if 'commands' in handler['filters']:
            key = handler['filters']['commands'][0]
            cmds[key] = handler['function']
    return cmds


# генерирует описание команд на основе docstring и создает командное меню
def setup_commands_menu(bt: TeleBot = bot):
    def doc(func):
        return func.__doc__ if func.__doc__ else '...'
    return bt.set_my_commands(
        [BotCommand(k, doc(v)) for k, v in get_actual_commands(bt).items()]
    )