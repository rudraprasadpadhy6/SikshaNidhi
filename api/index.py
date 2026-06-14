import os
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS

# Clear up local path loading constraints absolutely
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)

if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.append(PARENT_DIR)

try:
    from backend.db_helper import get_db_connection, is_postgres
except ImportError:
    try:
        from db_helper import get_db_connection, is_postgres
    except ImportError as e:
        raise ImportError(f"Pathing Error: Could not locate db_helper.py. Checked {CURRENT_DIR} and {PARENT_DIR}. Details: {e}")

app = Flask(__name__)
CORS(app)

def execute_query(conn, query, params=None):
    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        cursor.close()
    except Exception as e:
        print(f"Database setup notice: {e}")

def init_db():
    conn = get_db_connection()
    execute_query(conn, '''
        CREATE TABLE IF NOT EXISTS scholarships (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            scholarship_type TEXT,
            start_date TEXT,
            close_date TEXT,
            amount INTEGER,
            url TEXT,
            description TEXT,
            min_age INTEGER,
            max_age INTEGER,
            gender TEXT,
            caste TEXT,
            min_marks REAL,
            max_income REAL,
            pwd_only BOOLEAN DEFAULT FALSE,
            documents_required TEXT
        );
    ''')
    execute_query(conn, '''
        CREATE TABLE IF NOT EXISTS financial_schemes (
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
            priority INTEGER,
            documents_required TEXT
        );
    ''')
    conn.close()

# Safe initializer call
try:
    init_db()
except Exception as e:
    print(f"Deferred DB Initializer Check: {e}")


@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "message": "SikshaNidhi Engine Live",
        "environment": "PostgreSQL Cloud Cluster" if is_postgres() else "Local SQLite Backup"
    })


@app.route('/api/live_scholarships', methods=['GET'])
def live_scholarships():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, scholarship_type, close_date, amount, url, documents_required FROM scholarships;")
        rows = cursor.fetchall()
        
        data = []
        for row in rows:
            if isinstance(row, dict) or hasattr(row, 'get'):
                data.append({
                    "name": row.get("name"),
                    "type": row.get("scholarship_type"),
                    "close_date": str(row.get("close_date")),
                    "amt": row.get("amount"),
                    "url": row.get("url"),
                    "docs": row.get("documents_required"),
                    "status": "Ongoing"
                })
            else:
                data.append({
                    "name": row[0],
                    "type": row[1],
                    "close_date": str(row[2]),
                    "amt": row[3],
                    "url": row[4],
                    "docs": row[5],
                    "status": "Ongoing"
                })
                
        return jsonify({"data": data, "status": "success"}), 200
        
    except Exception as e:
        return jsonify({"data": [], "status": "error", "message": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@app.route('/api/live_schemes', methods=['GET'])
def live_schemes():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, description, official_website, priority FROM financial_schemes;")
        rows = cursor.fetchall()
        
        data = []
        for row in rows:
            if isinstance(row, dict) or hasattr(row, 'get'):
                data.append({
                    "name": row.get("name"),
                    "description": row.get("description"),
                    "url": row.get("official_website"),
                    "priority_score": row.get("priority")
                })
            else:
                data.append({
                    "name": row[0],
                    "description": row[1],
                    "url": row[2],
                    "priority_score": row[3]
                })
                
        return jsonify({"data": data, "status": "success"}), 200
        
    except Exception as e:
        return jsonify({"data": [], "status": "error", "message": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)