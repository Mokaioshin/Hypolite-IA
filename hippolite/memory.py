import sqlite3


DATABASE = "hipolite.db"


def init_memory():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def save_message(role, content):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO messages (role, content) VALUES (?, ?)",
        (role, content)
    )

    connection.commit()
    connection.close()


def get_recent_messages(limit=10):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT role, content
        FROM messages
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    messages = cursor.fetchall()
    connection.close()

    return list(reversed(messages))