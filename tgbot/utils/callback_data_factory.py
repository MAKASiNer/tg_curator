import json
from telebot.types import CallbackQuery, Message

from tgbot.data.models import CallbacksData


def make_callback_data(cmd: str, data: object = None) -> str:
    s = json.dumps([cmd, data], separators=(',', ':'))
    if len(s) > 63:
        return f'+{CallbacksData.get_or_create(json_str=s)[0].get_id()}'
    return f'-{s}'


def make_callback_query(msg: Message, cmd: str, data: object = None) -> CallbackQuery:
    return CallbackQuery(
        id=None,
        from_user=msg.from_user,
        data=make_callback_data(cmd, data),
        chat_instance=None,
        json_string=None,
        message=msg)


def parse_callback_data(s: str) -> tuple[str, object]:
    flag, s = s[:1], s[1:]
    if flag == '+':
        return json.loads(CallbacksData.get_by_id(pk=int(s)).json_str)
    return json.loads(s)


def parse_callback_query(query: CallbackQuery):
    return parse_callback_data(query.data)
