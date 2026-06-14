import os
from db_helper import get_db_connection, is_postgres

def init_feedback_db():
    conn = get_db_connection('feedback')
    c = conn.cursor()

    if is_postgres():
        c.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id SERIAL PRIMARY KEY,
                user_name TEXT DEFAULT 'Anonymous',
                rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
                category TEXT DEFAULT 'General',
                message TEXT NOT NULL,
                page TEXT DEFAULT 'Unknown',
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_read INTEGER DEFAULT 0
            )
        ''')
    else:
        c.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT DEFAULT 'Anonymous',
                rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
                category TEXT DEFAULT 'General',
                message TEXT NOT NULL,
                page TEXT DEFAULT 'Unknown',
                submitted_at TEXT DEFAULT (datetime('now', 'localtime')),
                is_read INTEGER DEFAULT 0
            )
        ''')

    conn.commit()
    conn.close()
    print("Feedback database ready.")

if __name__ == '__main__':
    init_feedback_db()
