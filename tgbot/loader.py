from telebot import TeleBot
from tgbot.data.config import TTOKEN


bot = TeleBot(TTOKEN, parse_mode='html')