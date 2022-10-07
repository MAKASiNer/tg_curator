import json
from pathlib import Path
from hashlib import sha256
from telebot import types

from tgbot.tools import logger


CACHE_PATH = './cache'

K_HASH_LEN = 1


__all__ = [
    'compile_callback_data',
    'parse_callback_data',
    'parse_callback_query'
]


def _filename_cache_dict() -> str:
    return sha256('кеш api ключей'.encode('utf-8')).hexdigest()


def _load_cache_dict() -> dict:
    folder = Path(CACHE_PATH)
    try:
        with open(folder / _filename_cache_dict(), 'rt+') as file:
            return json.load(file)
    except FileNotFoundError:
        folder.mkdir(exist_ok=True)
        return dict()


def _save_cache_dict(dct):
    folder = Path(CACHE_PATH)
    with open(folder / _filename_cache_dict(), 'wt') as file:
        return json.dump(dct, file)


_CACHE_DICT = _load_cache_dict()


def _encode_key(key: str) -> str:
    for _hash, k in _CACHE_DICT.items():
        if key == k:
            return _hash
    else:
        _hash = len(_CACHE_DICT).to_bytes(K_HASH_LEN, 'big').hex()
        _CACHE_DICT[_hash] = key
        _save_cache_dict(_CACHE_DICT)
        return _hash


def _decode_key(_hash: str) -> str:
    return _CACHE_DICT[_hash]


def _encode_value(data):
    if isinstance(data, dict):
        return {_encode_key(k): _encode_value(v) for k, v in data.items()}
    elif isinstance(data, (list, tuple)):
        return data.__class__(map(_decode_key, data))
    return data


def _decode_value(data):
    if isinstance(data, dict):
        return {_decode_key(k): _decode_value(v) for k, v in data.items()}
    elif isinstance(data, (list, tuple)):
        return data.__class__(map(_decode_key, data))
    return data


# компилирует данные калбека в строку
def compile_callback_data(cmd: str, data: dict = None):
    if not data:
        data = dict()

    s = json.dumps([_encode_key(cmd), _encode_value(data)],
                   separators=(',', ':'))

    print(f'{len(s)/len(json.dumps([cmd, data])):3.2%}')

    if len(s) > 64:
        logger.getLogger().error(f"length of '{s}' more than 64")

    return s


# декомпилирует данные строки
def parse_callback_data(s: str):
    try:

        k, v = json.loads(s)
        cmd: str = _decode_key(k)
        data: dict = _decode_value(v)
        return cmd, data
    except BaseException as err:
        logger.getLogger().exception('Callback data is invalid: %s', err, exc_info=True)


# декомпилируем данные из калбека
def parse_callback_query(call: types.CallbackQuery):
    return parse_callback_data(call.data)


if __name__ == '__main__':

    print(s := json.dumps(_encode_value({"c_id": 452, "msg_id": 593,
          "data": {'content': 'яйца', 'type': 'орган'}})))

    print(_decode_value(json.loads(s)))
