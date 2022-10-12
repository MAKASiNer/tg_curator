import json
from dataclasses import dataclass, fields, asdict
from telebot.types import CallbackQuery, Message

from tgbot.data.models import CallbacksData


def _make_callback_data(cmd: str, data: object = None) -> str:
    s = json.dumps([cmd, data], separators=(',', ':'))
    if len(s) > 63:
        return f'+{CallbacksData.get_or_create(json_str=s)[0].get_id()}'
    return f'-{s}'


def _make_callback_query(msg: Message, cmd: str, data: object = None) -> CallbackQuery:
    return CallbackQuery(
        id=None,
        from_user=msg.from_user,
        data=_make_callback_data(cmd, data),
        chat_instance=None,
        json_string=None,
        message=msg)


def _parse_callback_data(s: str) -> tuple[str, object]:
    flag, s = s[:1], s[1:]
    if flag == '+':
        return json.loads(CallbacksData.get_by_id(pk=int(s)).json_str)
    return json.loads(s)


def _parse_callback_query(query: CallbackQuery):
    return _parse_callback_data(query.data)


apiclass = dataclass(frozen=True)


@apiclass
class Api:

    @classmethod
    @property
    def keys(cls):
        return [f.name for f in fields(cls)]

    @property
    def values(self):
        return [getattr(self, f.name) for f in fields(self)]

    @property
    def items(self):
        return asdict(self)

    @classmethod
    @property
    def command(cls):
        return cls.__name__

    def make_callback_data(self):
        return _make_callback_data(self.command, self.items)

    def make_callback_query(self, msg: Message):
        return _make_callback_query(msg, self.command, self.items)

    @classmethod
    def parse_callback_data(cls, qdata: str):
        cmd, data = _parse_callback_data(qdata)
        if cmd != cls.command:
            raise RuntimeError("Callback command '%s' does not match '%s'" % (cmd, cls.command))
        return cls(**data)

    @classmethod
    def parse_callback_query(cls, query: CallbackQuery):
        return cls.parse_callback_data(query.data)

    @classmethod
    def filter(cls, q: CallbackQuery):
        return _parse_callback_query(q)[0] == cls.command
