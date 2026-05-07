import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'feedback.db')

def init_feedback_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

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
    print(f"Feedback database ready at {DB_PATH}")

if __name__ == '__main__':
    init_feedback_db()
