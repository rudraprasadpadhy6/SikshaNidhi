import os
import sys
import sqlite3
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

# We look for DATABASE_URL in the environment
DATABASE_URL = os.getenv('DATABASE_URL')

# SQLite fallback paths (relative to backend directory)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

SCHOLAR_DB = os.path.join(DATA_DIR, 'scholarships.db')
SCHEMES_DB = os.path.join(DATA_DIR, 'schemes.db')
# For feedback, use tmp on Vercel, local file otherwise
IS_VERCEL = os.getenv('VERCEL') == '1'
FEEDBACK_DB = '/tmp/feedback.db' if IS_VERCEL else os.path.join(DATA_DIR, 'feedback.db')

def is_postgres():
    return DATABASE_URL and (DATABASE_URL.startswith('postgres://') or DATABASE_URL.startswith('postgresql://'))

class PostgresCursorWrapper:
    def __init__(self, cursor):
        self._cursor = cursor
        self._lastrowid = None

    def execute(self, query, params=None):
        # Convert sqlite ? placeholders to psycopg2 %s placeholders
        query = query.replace('?', '%s')
        
        # Intercept INSERT queries to get the generated id for lastrowid
        is_insert = query.strip().upper().startswith('INSERT')
        if is_insert and 'RETURNING' not in query.upper():
            # Extract table name to form a proper RETURNING clause or generic RETURNING id
            query += ' RETURNING id'

        if params is not None:
            # psycopg2 expects tuples/lists for parameters; convert dict or keep as is
            self._cursor.execute(query, params)
        else:
            self._cursor.execute(query)

        if is_insert:
            try:
                row = self._cursor.fetchone()
                if row:
                    if isinstance(row, dict):
                        self._lastrowid = row.get('id')
                    else:
                        self._lastrowid = row[0]
            except Exception:
                pass

    def executemany(self, query, params_list):
        query = query.replace('?', '%s')
        self._cursor.executemany(query, params_list)

    def fetchone(self):
        row = self._cursor.fetchone()
        return row

    def fetchall(self):
        return self._cursor.fetchall()

    @property
    def lastrowid(self):
        return self._lastrowid

    @property
    def description(self):
        return self._cursor.description

    def close(self):
        self._cursor.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

class PostgresConnectionWrapper:
    def __init__(self, conn):
        self._conn = conn
        self._row_factory = None

    @property
    def row_factory(self):
        return self._row_factory

    @row_factory.setter
    def row_factory(self, val):
        self._row_factory = val

    def cursor(self):
        from psycopg2.extras import RealDictCursor
        cur = self._conn.cursor(cursor_factory=RealDictCursor)
        return PostgresCursorWrapper(cur)

    def execute(self, query, params=None):
        cur = self.cursor()
        cur.execute(query, params)
        return cur

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
        self.close()

# We export a unified get_db_connection function
def get_db_connection(db_name_or_path=None):
    """
    Returns a database connection. If DATABASE_URL is set to PostgreSQL,
    it returns a wrapper connection to PostgreSQL (sharing the same database).
    Otherwise, it returns a local sqlite3 connection.
    """
    global DATABASE_URL
    # Reload environment variable in case it was written during runtime
    load_dotenv()
    DATABASE_URL = os.getenv('DATABASE_URL')

    if is_postgres():
        import psycopg2
        url = DATABASE_URL
        # Normalize protocol if needed
        if url.startswith('postgres://'):
            url = url.replace('postgres://', 'postgresql://', 1)
        conn = psycopg2.connect(url)
        return PostgresConnectionWrapper(conn)
    else:
        # Resolve SQLite path
        path = db_name_or_path
        if not path:
            path = SCHOLAR_DB
        elif 'scholarships' in path:
            path = SCHOLAR_DB
        elif 'schemes' in path:
            path = SCHEMES_DB
        elif 'feedback' in path:
            path = FEEDBACK_DB
            
        conn = sqlite3.connect(path)
        # Enable dict-style column access (r['col_name']) for all SQLite connections
        conn.row_factory = sqlite3.Row
        return conn
