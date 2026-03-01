import sqlite3

conn = sqlite3.connect("music.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS queues (
    guild_id INTEGER,
    url TEXT
)
""")
conn.commit()


def add_song(guild_id, url):
    cursor.execute("INSERT INTO queues VALUES (?, ?)", (guild_id, url))
    conn.commit()


def get_queue(guild_id):
    cursor.execute("SELECT url FROM queues WHERE guild_id=?", (guild_id,))
    return [row[0] for row in cursor.fetchall()]


def remove_first(guild_id):
    cursor.execute("""
    DELETE FROM queues
    WHERE rowid IN (
        SELECT rowid FROM queues WHERE guild_id=? LIMIT 1
    )
    """, (guild_id,))
    conn.commit()


def clear_queue(guild_id):
    cursor.execute("DELETE FROM queues WHERE guild_id=?", (guild_id,))
    conn.commit()
