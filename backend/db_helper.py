import os
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3

def is_postgres():
    """Checks if a remote PostgreSQL cloud database string is configured."""
    url = os.getenv("postgresql://neondb_owner:npg_4BPEOv9wrdQe@ep-bitter-mouse-ah5rd0il.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require")
    return url is not None and (url.startswith("postgres://") or url.startswith("postgresql://"))

class ProductionPostgresAdapter:
    """Wraps a PostgreSQL connection to standardize cursor vending."""
    def __init__(self, conn):
        self.conn = conn

    def cursor(self, *args, **kwargs):
        # Enforce RealDictCursor so rows behave like dictionaries natively
        return ProductionCursorWrapper(self.conn.cursor(cursor_factory=RealDictCursor))

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()

class ProductionCursorWrapper:
    """
    An explicit query driver that bridges the gap between SQLite syntax 
    and PostgreSQL strict typing rules.
    """
    def __init__(self, cursor):
        self.cursor = cursor
        self.description = None

    def execute(self, query, params=None):
        # Uniformly convert standard question mark placeholders to Postgres %s format
        query = query.replace("?", "%s")
        
        if params:
            # Clean individual positional structures safely
            cleaned = []
            for p in params:
                if p == 0 and not isinstance(p, bool):
                    cleaned.append(False)
                elif p == 1 and not isinstance(p, bool):
                    cleaned.append(True)
                else:
                    cleaned.append(p)
            params = tuple(cleaned)
            
        try:
            self.cursor.execute(query, params)
            self.description = self.cursor.description
            return self
        except Exception as e:
            raise e

    def executemany(self, query, params_list):
        """
        Intercepts data tuples during batch insertion to convert raw integer flags 
        (0 and 1) to explicit boolean literals (False and True) for PostgreSQL.
        """
        query = query.replace("?", "%s")
        cleaned_params = []
        
        for params in params_list:
            new_row = []
            for p in params:
                # Intercept integer representations to satisfy strict boolean constraints
                if p == 0 and not isinstance(p, bool):
                    new_row.append(False)
                elif p == 1 and not isinstance(p, bool):
                    new_row.append(True)
                else:
                    new_row.append(p)
            cleaned_params.append(tuple(new_row))

        try:
            self.cursor.executemany(query, cleaned_params)
            self.description = self.cursor.description
            return self
        except Exception as e:
            raise e

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

def get_db_connection(target_type='default'):
    """
    The main connection orchestrator. Automatically resolves your current environment 
    state to connect to local backup instances or cloud systems smoothly.
    """
    url = os.getenv("DATABASE_URL")
    if is_postgres():
        # Fix deprecated Heroku/Render URI prefixes gracefully
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        conn = psycopg2.connect(url)
        return ProductionPostgresAdapter(conn)
    else:
        # Local development environment fallback layer
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, f"{target_type}.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn