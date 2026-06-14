import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for frontend compatibility

# Initialize Groq client using environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# ── DATABASE CONFIGURATION & ENVIRONMENT HELPERS ────────────────────────────
def get_db_url():
    """Fetches the PostgreSQL connection URL from the environment."""
    return os.getenv("DATABASE_URL")

def is_postgres():
    """Returns True if a remote PostgreSQL connection string is configured."""
    url = get_db_url()
    return url is not None and (url.startswith("postgres://") or url.startswith("postgresql://"))

class PostgresSQLiteAdapter:
    """
    An adapter that wraps a PostgreSQL connection/cursor to mimic SQLite's behavior,
    automatically mapping SQLite query syntax and data patterns to PostgreSQL standards.
    """
    def __init__(self, pg_conn):
        self.conn = pg_conn

    def execute(self, query, params=None):
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        
        # 1. Translate SQLite syntax components to clean PostgreSQL alternatives
        query = query.replace("?", "%s")
        query = query.replace("LIKE", "ILIKE")
        query = query.replace("AUTOINCREMENT", "SERIAL")
        
        # 2. Rectify typical SQLite boolean literal mismatches
        if params:
            new_params = []
            for p in params:
                if p == "TRUE" or p == "1":
                    new_params.append(True)
                elif p == "FALSE" or p == "0":
                    new_params.append(False)
                else:
                    new_params.append(p)
            params = tuple(new_params)

        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor
        except Exception as e:
            self.conn.rollback()
            raise e

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

def get_db_connection(target_type='default'):
    """
    Central connection router. Resolves to a native SQLite file or 
    safely provisions a unified PostgreSQL connection adapter.
    """
    if is_postgres():
        url = get_db_url()
        # Fix for old Heroku/Render configurations that use the deprecated 'postgres://' prefix
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        pg_conn = psycopg2.connect(url)
        return PostgresSQLiteAdapter(pg_conn)
    else:
        # Fallback local environment backup
        db_path = os.path.join('/tmp', f"{target_type}.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

# ── AUTOMATED DATABASE INITIALIZATION ON SERVER STARTUP ──────────────────────
def _init_production_tables():
    """
    Guarantees that your Neon Cloud PostgreSQL architecture contains all your 
    required data tables before any app request can ever run into a missing table error.
    """
    print("Checking database schemas and initializing tables inside Neon...")
    
    # 1. Initialize Scholarships Table
    try:
        conn = get_db_connection('scholarships')
        conn.execute('''CREATE TABLE IF NOT EXISTS scholarships (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            scholarship_type TEXT,
            start_date TEXT,
            close_date TEXT,
            amount INTEGER,
            url TEXT,
            description TEXT,
            min_age INTEGER DEFAULT 0,
            max_age INTEGER DEFAULT 100,
            gender TEXT DEFAULT 'All',
            caste TEXT DEFAULT 'All',
            min_marks INTEGER DEFAULT 0,
            max_income INTEGER DEFAULT 99999999,
            pwd_only BOOLEAN DEFAULT FALSE,
            documents_required TEXT
        )''')
        conn.commit()
        conn.close()
        print("✓ Scholarships schema synchronized.")
    except Exception as e:
        print(f"Error preparing scholarships schema: {e}")

    # 2. Initialize Financial Schemes Table
    try:
        conn = get_db_connection('schemes')
        conn.execute('''CREATE TABLE IF NOT EXISTS financial_schemes (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            long_description TEXT,
            why_chosen TEXT,
            official_website TEXT,
            target_states TEXT,
            min_age INTEGER,
            max_age INTEGER,
            marital_status TEXT,
            categories TEXT,
            disability_required BOOLEAN DEFAULT FALSE,
            education_levels TEXT,
            employment_statuses TEXT,
            priority INTEGER DEFAULT 5,
            documents_required TEXT
        )''')
        conn.commit()
        conn.close()
        print("✓ Financial Schemes schema synchronized.")
    except Exception as e:
        print(f"Error preparing financial schemes schema: {e}")

    # 3. Initialize Feedback Tracker Table
    try:
        conn = get_db_connection('feedback')
        conn.execute('''CREATE TABLE IF NOT EXISTS feedback (
            id SERIAL PRIMARY KEY,
            user_name TEXT,
            rating INTEGER,
            category TEXT,
            message TEXT,
            page TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        conn.commit()
        conn.close()
        print("✓ Feedback schemas synchronized successfully.")
    except Exception as e:
        print(f"Error preparing feedback schema: {e}")

# Run schema validation immediately upon deployment bootup
_init_production_tables()

# ── ENDPOINTS / ROUTE HANDLERS ──────────────────────────────────────────────

@app.route('/api/live_scholarships', methods=['GET'])
def get_live_scholarships():
    """Fetches full data directly out of your cloud table storage."""
    try:
        conn = get_db_connection('scholarships')
        cursor = conn.execute("SELECT * FROM scholarships ORDER BY id DESC")
        rows = cursor.fetchall()
        
        # Convert raw row entries safely into serializeable standard python dict format
        results = [dict(row) for row in rows]
        conn.close()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/search', methods=['POST'])
def search_scholarships():
    """Filters data assets dynamically through multiple custom user vectors."""
    try:
        data = request.json or {}
        age = int(data.get('age', 18))
        gender = data.get('gender', 'All')
        caste = data.get('caste', 'All')
        marks = int(data.get('marks', 0))
        income = int(data.get('income', 99999999))
        pwd = data.get('pwd', False)

        conn = get_db_connection('scholarships')
        
        # Flexible multi-tiered parameter query composition
        query = """
            SELECT * FROM scholarships 
            WHERE min_age <= ? AND max_age >= ?
              AND (gender = 'All' OR gender = ?)
              AND (caste = 'All' OR caste = ?)
              AND min_marks <= ?
              AND max_income >= ?
              AND pwd_only = ?
        """
        params = (age, age, gender, caste, marks, income, "1" if pwd else "0")
        
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        results = [dict(row) for row in rows]
        conn.close()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Logs user metrics smoothly into your database records."""
    try:
        data = request.json or {}
        user_name = data.get('user_name', 'Anonymous')
        rating = data.get('rating')
        category = data.get('category', 'General')
        message = data.get('message', '')
        page = data.get('page', 'Unknown')

        conn = get_db_connection('feedback')
        query = "INSERT INTO feedback (user_name, rating, category, message, page) VALUES (?, ?, ?, ?, ?)"
        conn.execute(query, (user_name, rating, category, message, page))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Feedback recorded successfully"}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def ai_chat():
    """Processes conversational context prompts and routes through Groq Llama-3.1."""
    if not groq_client:
        return jsonify({"status": "error", "message": "AI services are not currently configured."}), 503
        
    try:
        data = request.json or {}
        user_message = data.get('message', '')
        history = data.get('history', [])

        messages = [{"role": "system", "content": "You are PixaBot, the official helpful AI concierge of SikshaNidhi. Assist students intelligently with Indian scholarship and educational financial scheme guidelines."}]
        for msg in history:
            messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
        messages.append({"role": "user", "content": user_message})

        completion = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages,
            temperature=0.7,
            max_tokens=1024
        )
        
        ai_response = completion.choices[0].message.content
        return jsonify({"status": "success", "response": ai_response}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Continuous production execution listener loop wrapper
if __name__ == '__main__':
    port = int(os.getenv("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)