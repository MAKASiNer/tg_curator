import logging
from datetime import datetime, timedelta

from tgbot.data.models import Sessions


logging.basicConfig(level=logging.INFO, format="[%(asctime)s] - %(message)s")
logger = logging.getLogger()


# возвращает сессию пользователя
def get_session(user_id: int) -> Sessions:
    session: Sessions = Sessions.get_or_create(user_id=user_id)[0]
    return session


# обновляет время сессии
def update_session(session_id: int):
    session: Sessions = Sessions.get(id=session_id)
    session.last_activity = datetime.now()
    session.save()


def register_admin_session(func=None, *, timeout=60, callback=None, args=None, kwargs=None):
    '''
    Регистрирует активность админов. По истечению таймаута блокирует выполнение функции

    Args:
        timeout  : int | float     - время в секундах за которое истекает сессия
        callback : function | None - функция-фальтернатива. Она должна принимать минимум 1 аргумент - сообщение или калбек
        args     : list | None     - args для callback
        kwargs   : dict | None     - kwargs для callback
    '''

    def decorator(func):
        def wrap(msg_or_query, *func_args, **func_kwargs):
            session = get_session(msg_or_query.from_user.id)
            delta = datetime.now() - session.last_activity
            logger.info("superuser: %s elapsed: %s", session.user.id, delta)

            if delta < timedelta(seconds=timeout):
                update_session(session.id)
                return func(msg_or_query, *func_args, **func_kwargs)

            elif callback is not None:
                return callback(msg_or_query, *(list() if not args else args), **(dict() if not kwargs else kwargs))

            else:
                return None

        return wrap

    if func is None:
        return decorator

    return decorator(func)
