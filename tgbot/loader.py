from telebot import TeleBot
from telebot.types import BotCommand

from tgbot.data.config import TG_TOKEN


bot = TeleBot(TG_TOKEN, parse_mode='html')

# бот будет покидать групповые чаты
bot.register_message_handler(lambda m: bot.leave_chat(m.chat.id), chat_types=['group', 'supergroup', 'channel'])


# словарь акруальных команд
def get_actual_commands(bt: TeleBot = bot) -> dict[str, ]:
    cmds = dict()
    for handler in bt.message_handlers:
        if 'commands' in handler['filters']:
            key = handler['filters']['commands'][0]
            cmds[key] = handler['function']
    return cmds


# создаем меню команд
def setup_commands_menu(bt: TeleBot = bot):
    def _mkdoc(func): return func.__doc__ if func.__doc__ else '...'
    bot.set_my_commands(
        [BotCommand(k, _mkdoc(v)) for k, v in get_actual_commands().items()]
    )
