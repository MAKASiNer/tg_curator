from hashlib import sha256


# возвращает хеш пароля
def secured_password(password: str):
    return sha256(password.encode('utf-8'), usedforsecurity=True).hexdigest()