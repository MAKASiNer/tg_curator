'''
Структура базы данных

Таблицы:

    courses:

    pages:

    tests:

'''

import sqlite3


# создает коннект к базе данных
def open_db():
    return sqlite3.Connection(
        'database.db',
        check_same_thread=False)


if __name__ == '__main__':
    cursor = sqlite3.Cursor(open_db())

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(255) NOT NULL,
            z_index INTEGER
        );
    ''')
