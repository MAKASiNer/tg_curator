import json
from telebot.types import CallbackQuery, Message

from tgbot.models import CallbacksData


def make_callback_data(cmd: str, data: object = None) -> int:
    return CallbacksData.create(json_str=json.dumps([cmd, data])).get_id()


def make_callback_query(msg: Message, cmd: str, data: object = None) -> CallbackQuery:
    return CallbackQuery(
        id=None,
        from_user=msg.from_user,
        data=make_callback_data(cmd, data),
        chat_instance=None,
        json_string=None,
        message=msg)


def parse_callback_data(pk: int) -> tuple[str, object]:
    return json.loads(CallbacksData.get_by_id(pk).json_str)


def parse_callback_query(query: CallbackQuery):
    return parse_callback_data(query.data)
