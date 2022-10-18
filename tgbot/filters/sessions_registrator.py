import logging
from datetime import datetime, timedelta

from tgbot.data.models import Users, SuperuserSessions


logging.basicConfig(level=logging.INFO, format="[%(asctime)s] - %(message)s")
logger = logging.getLogger()


# возвращает сессию пользователя
def get_superuser_session(user_id: int) -> SuperuserSessions:
    session: SuperuserSessions = SuperuserSessions.get_or_none(user_id=user_id)
    if not session:
        session = SuperuserSessions(user_id=user_id, last_activity=datetime.now())
        session.save()
    return session


# обновляет время сессии
def update_superuser_session(session_id: int):
    session: SuperuserSessions = SuperuserSessions.get(id=session_id)
    session.last_activity = datetime.now()
    session.save()


def register_superuser_session(func=None, *, timeout=60, callback=None):
    '''
    Регистрирует активность админов. По истечению таймаута блокирует выполнение функции

    Args:
        timeout  : int | float     - время в секундах за которое истекает сессия
        callback : function | None - функция-фальтернатива. Она должна принимать те же аргументы, что и основная функция
    '''

    def decorator(func):
        def wrap(msg_or_query, *args, **kwargs):
            session = get_superuser_session(msg_or_query.from_user.id)
            delta = datetime.now() - session.last_activity
            logger.info("SUPERUSER %s (elapsed %s) %s", session.user.username, delta, type(msg_or_query))

            if delta < timedelta(seconds=timeout):
                update_superuser_session(session.id)
                return func(msg_or_query, *args, **kwargs)

            elif callback is not None:
                return callback(msg_or_query, *args, **kwargs)

            else:
                return None

        return wrap

    if func is None:
        return decorator

    return decorator(func)


def register_user_session(func):
    '''
    Регистрирует действия обычного пользователя
    '''
    def wrap(msg_or_query, *func_args, **func_kwargs):

        user = Users.get_or_create(id=msg_or_query.from_user.id, username=msg_or_query.from_user.full_name)[0]

        logger.info("%s: %s", user.username, type(msg_or_query))
        return func(msg_or_query, *func_args, **func_kwargs)
    return wrap
