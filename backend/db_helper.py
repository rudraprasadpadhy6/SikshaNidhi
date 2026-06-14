import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor

def is_postgres():
    """Returns True if a live cloud connection string is available."""
    # This forces checking both Render's env and local configurations
    return "DATABASE_URL" in os.environ and os.environ["DATABASE_URL"].strip() != ""

def get_db_connection(db_type=None):
    """
    Dynamically routes connections. 
    Prioritizes production cloud PostgreSQL over local file backups.
    """
    if is_postgres():
        print("🛜 Connecting directly to Neon Cloud PostgreSQL Cluster...")
        url = os.environ["DATABASE_URL"]
        # Handle protocol variance if present
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        
        # Connect using the dictionary-mapping cursor format so code fields map dynamically
        return psycopg2.connect(url, cursor_factory=RealDictCursor)
    
    else:
        print("📦 Falling back to local SQLite environment database...")
        db_path = "backend/scholarships.db" if os.path.exists("backend") else "scholarships.db"
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn