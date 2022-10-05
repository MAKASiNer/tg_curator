import json
from telebot import types

from tgbot.tools import logger


__all__ = [
    'make_callback_data',
    'parse_callback_data',
    'parse_callback_query'
]


# компилирует данные калбека в строку
def make_callback_data(cmd: str, data: dict = None):
    if not data:
        data = dict()
    return json.dumps([cmd, data])


# парсит данные калбека из строки
def parse_callback_data(s: str):
    cmd: str
    data: dict

    try:
        cmd, data = json.loads(s)
    except BaseException as err:
        logger.getLogger().exception('Callback data is invalid: %s', err, exc_info=True)
        cmd, data = None, None

    return cmd, data


# парсит калбек напрямую
def parse_callback_query(call: types.CallbackQuery):
    return parse_callback_data(call.data)
