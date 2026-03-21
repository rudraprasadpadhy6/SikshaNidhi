from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import sqlite3
import os
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', '..', 'data', 'scholarships.db')
FRONTEND_PATH = os.path.join(BASE_DIR, '..', '..', 'frontend', 'unischolar', 'index.html')

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend connectivity

def get_scholarships(payload):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # 1. Extract values from frontend payload with defaults
    gender = payload.get('gender', 'Other')
    # Convert inputs to appropriate numeric types
    try: age = int(payload.get('age', 0))
    except (ValueError, TypeError): age = 0
    
    caste = payload.get('caste', 'All')
    pwd_status = payload.get('pwd', 'no')
    stype = payload.get('type') # 'Government' or 'Private' or None
    
    try: marks = int(payload.get('marks', 0))
    except (ValueError, TypeError): marks = 0
    
    try: income = int(payload.get('income', 99999999))
    except (ValueError, TypeError): income = 99999999
    
    # 2. Base Query mapping eligibility logic
    query = '''
        SELECT * FROM scholarships
        WHERE (min_age <= ? AND max_age >= ?)
        AND (gender = 'All' OR gender = ?)
        AND (caste = 'All' OR caste = ?)
        AND min_marks <= ?
        AND max_income >= ?
    '''
    params = [age, age, gender, caste, marks, income]

    # If category is selected, filter by type
    if stype:
        query += " AND scholarship_type = ?"
        params.append(stype)
    
    # If not a PWD student, hide PWD-only scholarships
    if pwd_status.lower() == 'no':
        query += " AND pwd_only = False"
        
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    
    # 3. Format response specifically for s1.html
    results = []
    today = datetime.now().strftime('%Y-%m-%d')
    for r in rows:
        # We append the type [Gov] / [Private] to the name so the user 
        # clearly sees the distinction in the frontend grid without changing the HTML code.
        type_prefix = "[Government]" if r['scholarship_type'] == 'Government' else "[Private]"
        status_label = "Live" if r['close_date'] >= today else "Expired"
        
        # Custom detailed info
        detailed_info = (
            f"Scholarship Type: {r['scholarship_type']}\n"
            f"Start Date: {r['start_date']}\n"
            f"Close Date: {r['close_date']}\n"
            f"Reward Amount: Rs.{r['amount']:,}\n"
            f"Official Website: {r['url']}\n"
            f"----------------------------------------\n"
            f"In Details: {r['description']}"
        )
        
        results.append({
            'name': f"{type_prefix} {r['name']} [{status_label}]",
            'amt': r['amount'],
            'ds': detailed_info,
            'end': r['close_date'],
            'end_date': r['close_date'],
            'url': r['url'],
            'type': r['scholarship_type'],
            'status': status_label
        })
    
    return results

@app.route('/')
def index():
    try:
        with open(FRONTEND_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error loading frontend/unischolar/index.html: {e}", 500

@app.route('/api/search', methods=['POST'])
def search_scholarships():
    try:
        payload = request.json
        if not payload:
            return jsonify({"status": "error", "message": "No payload provided."}), 400
            
        matches = get_scholarships(payload)
        # Use json.dumps with ensure_ascii=False to safely handle any unicode chars
        response_body = json.dumps({"status": "success", "data": matches}, ensure_ascii=False)
        return Response(response_body, status=200, mimetype='application/json; charset=utf-8')
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("Starting UniScholar API Server on port 5000...")
    app.run(debug=True, port=5000)
