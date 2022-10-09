from tgbot.loader import bot
from tgbot.handlers import *
from tgbot.utils.bot_utils import setup_commands_menu

setup_commands_menu(bot)
bot.infinity_polling()
