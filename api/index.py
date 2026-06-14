import json
import sqlite3
import re
import base64
import asyncio
import sys
import os
import csv
import io
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from dotenv import load_dotenv

# Handle directory lookup safely across local, Vercel, and Render layouts
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

sys.path.append(parent_dir)
if os.path.exists(os.path.join(parent_dir, 'backend')):
    sys.path.append(os.path.join(parent_dir, 'backend'))

from db_helper import get_db_connection, is_postgres

load_dotenv()

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
ADMIN_KEY    = os.getenv('ADMIN_FEEDBACK_KEY', 'siksha-admin-2026')

# ── HELPER FUNCTION FOR AUTOMATIC POSTGRESQL COMPATIBILITY ──
def execute_query(conn, query, params=None):
    """
    Automated wrapper that converts SQLite style '?' placeholders to PostgreSQL '%s' 
    and handles boolean keywords automatically if running on the Neon cloud database.
    """
    if params is None:
        params = ()
    
    if is_postgres():
        query = query.replace('?', '%s')
        query = query.replace('= False', '= FALSE')
        query = query.replace('= True', '= TRUE')
        
    cursor = conn.cursor()
    cursor.execute(query, params)
    return cursor

def convert_row(cursor, row):
    """Safely converts database cursor results into standard python dictionaries."""
    if is_postgres():
        return dict(zip([col[0] for col in cursor.description], row))
    return dict(row)

# ── Automated Database Tables Creation on Bootup ──────────────────────────────
def _init_production_tables():
    print("Verifying database schema inside Neon PostgreSQL...")
    
    # 1. Initialize Feedback Table
    conn = get_db_connection('feedback')
    if is_postgres():
        execute_query(conn, '''CREATE TABLE IF NOT EXISTS feedback (
            id           SERIAL PRIMARY KEY,
            user_name    TEXT    DEFAULT 'Anonymous',
            rating       INTEGER NOT NULL,
            category     TEXT    DEFAULT 'General',
            message      TEXT    NOT NULL,
            page         TEXT    DEFAULT 'Unknown',
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_read      INTEGER DEFAULT 0
        )''')
    else:
        conn.execute('''CREATE TABLE IF NOT EXISTS feedback (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name    TEXT    DEFAULT 'Anonymous',
            rating       INTEGER NOT NULL,
            category     TEXT    DEFAULT 'General',
            message      TEXT    NOT NULL,
            page         TEXT    DEFAULT 'Unknown',
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_read      INTEGER DEFAULT 0
        )''')
    conn.commit()
    conn.close()

    # 2. Initialize Scholarships Table
    conn = get_db_connection('scholarships')
    if is_postgres():
        execute_query(conn, '''CREATE TABLE IF NOT EXISTS scholarships (
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

    # 3. Initialize Financial Schemes Table
    conn = get_db_connection('schemes')
    if is_postgres():
        execute_query(conn, '''CREATE TABLE IF NOT EXISTS financial_schemes (
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
    print("✓ All tables initialized successfully!")

_init_production_tables()

# =============================================================================
# SCHOLAR SERVER
# =============================================================================
def _get_scholarships(payload):
    conn = get_db_connection('scholarships')
    conn.row_factory = getattr(conn, 'row_factory', None)
    gender = payload.get('gender', 'Other')
    try:   age    = int(payload.get('age',    0))
    except: age   = 0
    try:   marks  = int(payload.get('marks',  0))
    except: marks = 0
    try:   income = int(payload.get('income', 99999999))
    except: income = 99999999
    caste      = payload.get('caste', 'All')
    pwd_status = payload.get('pwd',   'no')
    stype      = payload.get('type')

    q = '''SELECT * FROM scholarships
           WHERE (min_age <= ? AND max_age >= ?)
             AND (gender = 'All' OR gender = ?)
             AND (caste  = 'All' OR caste  = ?)
             AND min_marks  <= ?
             AND max_income >= ?'''
    params = [age, age, gender, caste, marks, income]
    if stype:
        q += ' AND scholarship_type = ?'; params.append(stype)
    if pwd_status.lower() == 'no':
        q += ' AND pwd_only = False'

    c = execute_query(conn, q, params)
    rows = c.fetchall(); conn.close()
    today  = datetime.now().strftime('%Y-%m-%d')
    result = []
    for r in rows:
        r_dict = convert_row(c, r)
        tpfx   = '[Government]' if r_dict['scholarship_type'] == 'Government' else '[Private]'
        status = 'Live' if r_dict['close_date'] >= today else 'Expired'
        info   = (f"Scholarship Type: {r_dict['scholarship_type']}\n"
                  f"Start Date: {r_dict['start_date']}\nClose Date: {r_dict['close_date']}\n"
                  f"Reward Amount: Rs.{r_dict['amount']:,}\nOfficial Website: {r_dict['url']}\n"
                  f"----------------------------------------\nIn Details: {r_dict['description']}")
        result.append({'name': f"{tpfx} {r_dict['name']} [{status}]", 'amt': r_dict['amount'],
                       'ds': info, 'end': r_dict['close_date'], 'end_date': r_dict['close_date'],
                       'url': r_dict['url'], 'type': r_dict['scholarship_type'],
                       'status': status, 'docs': r_dict['documents_required']})
    return result


@app.route('/api/search', methods=['POST'])
def search_scholarships():
    try:
        payload = request.json
        if not payload:
            return jsonify({'status': 'error', 'message': 'No payload provided.'}), 400
        matches = _get_scholarships(payload)
        body = json.dumps({'status': 'success', 'data': matches}, ensure_ascii=False)
        return Response(body, status=200, mimetype='application/json; charset=utf-8')
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    try:
        conn = get_db_connection('scholarships')
        conn.row_factory = getattr(conn, 'row_factory', None)
        today = datetime.now()
        t0 = today.strftime('%Y-%m-%d')
        t5 = (today + timedelta(days=5)).strftime('%Y-%m-%d')
        c = execute_query(conn, 'SELECT name,close_date,url,documents_required FROM scholarships WHERE close_date>=? AND close_date<=?', (t0, t5))
        rows = c.fetchall(); conn.close()
        out = []
        for r in rows:
            r_dict = convert_row(c, r)
            dl = (datetime.strptime(r_dict['close_date'], '%Y-%m-%d') - today).days + 1
            out.append({'name': r_dict['name'], 'days_left': dl, 'url': r_dict['url'], 'docs': r_dict['documents_required']})
        return jsonify({'status': 'success', 'notifications': out})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/live_scholarships', methods=['GET'])
def get_live_scholarships():
    try:
        conn = get_db_connection('scholarships')
        conn.row_factory = getattr(conn, 'row_factory', None)
        today = datetime.now().strftime('%Y-%m-%d')
        c = execute_query(conn, 'SELECT name,close_date,url,amount,scholarship_type,documents_required FROM scholarships WHERE close_date>=? ORDER BY close_date ASC LIMIT 10', (today,))
        rows = c.fetchall(); conn.close()
        live = []
        for r in rows:
            r_dict = convert_row(c, r)
            live.append({'name': r_dict['name'], 'close_date': r_dict['close_date'], 'url': r_dict['url'],
                         'amt': r_dict['amount'], 'type': r_dict['scholarship_type'],
                         'status': 'Ongoing', 'docs': r_dict['documents_required']})
        return jsonify({'status': 'success', 'data': live})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# =============================================================================
# CAPITAL SERVER
# =============================================================================
def _build_scheme_html(scheme):
    sid = scheme['id']
    return f'''
<span style="cursor:pointer;color:#054c5a;text-decoration:underline;display:block;padding:5px 0;"
      onclick="if(window.event)window.event.preventDefault();
               const t=document.getElementById('details-{sid}').innerHTML;
               const c=document.getElementById('success-screen');
               if(!window.originalListCache)window.originalListCache=c.innerHTML;
               c.innerHTML=t;">
  {scheme['name']} <small style="color:#4dcbc6;font-size:14px;margin-left:10px;font-weight:normal;">(Click for details)</small>
</span>
<template id="details-{sid}">
  <div style="text-align:left;padding:10px;font-family:'Segoe UI',sans-serif;">
    <h2 style="color:#0b5b6a;margin-bottom:15px;font-size:34px;">{scheme['name']}</h2>
    <p style="color:#666;font-size:20px;margin-bottom:35px;">{scheme['description']}</p>
    <div style="background:#e8f8f9;padding:25px;border-radius:12px;margin-bottom:25px;">
      <h3 style="color:#0b5b6a;margin-top:0;font-size:22px;">About This Opportunity</h3>
      <p style="color:#444;font-size:18px;line-height:1.6;">{scheme['long_description']}</p>
    </div>
    <div style="background:#e8f8f9;padding:25px;border-radius:12px;margin-bottom:40px;">
      <h3 style="color:#0b5b6a;margin-top:0;font-size:22px;">Why We Chose This For You</h3>
      <p style="color:#444;font-size:18px;line-height:1.6;">{scheme['why_chosen']}</p>
    </div>
    <div style="display:flex;gap:20px;">
      <button onclick="document.getElementById('success-screen').innerHTML=window.originalListCache;window.originalListCache=null;"
              style="background:#e8f8f9;color:#4dcbc6;padding:20px 30px;font-size:22px;font-weight:600;border:none;border-radius:12px;cursor:pointer;flex:1;">
        Back to List
      </button>
      <a href="{scheme['official_website']}" target="_blank"
         style="background:#4dcbc6;color:white;padding:20px 30px;font-size:22px;font-weight:600;border:none;border-radius:12px;cursor:pointer;text-decoration:none;text-align:center;flex:1;display:inline-block;">
        Official Website
      </a>
    </div>
  </div>
</template>'''


@app.route('/api/find-opportunities', methods=['POST', 'OPTIONS'])
def find_opportunities():
    if request.method == 'OPTIONS':
        r = jsonify({}); r.headers.update({'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'}); return r
    try:
        data = request.json or {}
        age          = int(data.get('age', 0))
        state        = data.get('state', '')
        marital      = data.get('maritalStatus', '')
        category     = data.get('category', '')
        disability   = data.get('disability', 'No') == 'Yes'
        education    = data.get('education', '')
        employment   = data.get('employment', '')

        conn = get_db_connection('schemes')
        c = execute_query(conn, 'SELECT * FROM financial_schemes')
        columns = [col[0] for col in c.description]
        rows = c.fetchall(); conn.close()

        eligible = []
        for row in rows:
            s = dict(zip(columns, row))
            if s['min_age'] is not None and age < s['min_age']: continue
            if s['max_age'] is not None and age > s['max_age']: continue
            ts = json.loads(s['target_states'] or '["ALL"]')
            if 'ALL' not in ts and state not in ts: continue
            vms = json.loads(s['marital_status'] or '[]')
            if vms and marital not in vms: continue
            vc = json.loads(s['categories'] or '[]')
            if vc and category not in vc: continue
            if s['disability_required'] and not disability: continue
            ve = json.loads(s['education_levels'] or '[]')
            if ve and education not in ve: continue
            vemp = json.loads(s['employment_statuses'] or '[]')
            if vemp and employment not in vemp: continue
            eligible.append({'name': _build_scheme_html(s), 'description': s['description'],
                             'official_website': s['official_website'], 'priority': s['priority'],
                             'docs': s.get('documents_required', '1. Aadhar Card\n2. Income Certificate\n3. Bank Passbook')})

        eligible.sort(key=lambda x: x['priority'], reverse=True)
        return jsonify({'success': True, 'count': len(eligible), 'opportunities': eligible})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/add-opportunity', methods=['POST', 'OPTIONS'])
def add_opportunity():
    if request.method == 'OPTIONS':
        r = jsonify({}); r.headers.update({'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST,OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'}); return r
    try:
        data = request.json or {}
        conn = get_db_connection('schemes')
        q = '''INSERT INTO financial_schemes
            (name,description,long_description,why_chosen,official_website,target_states,
             min_age,max_age,marital_status,categories,disability_required,
             education_levels,employment_statuses,priority)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''
        params = (data.get('name','Untitled'), data.get('description',''),
             data.get('long_description',''), data.get('why_chosen',''),
             data.get('official_website',''), json.dumps(data.get('target_states',['ALL'])),
             data.get('min_age'), data.get('max_age'),
             json.dumps(data.get('marital_status',[])), json.dumps(data.get('categories',[])),
             data.get('disability_required', False),
             json.dumps(data.get('education_levels',[])),
             json.dumps(data.get('employment_statuses',[])), data.get('priority',5))
        
        c = execute_query(conn, q, params)
        conn.commit(); conn.close()
        return jsonify({'success': True, 'message': 'Added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =============================================================================
# PIXABOT
# =============================================================================
_standard_memory = {}
_therapy_memory  = {}

_STANDARD_PROMPT = """You are Pixa, an interactive educational advisor for the ShikshaNidhi app.
CURRENT EXACT DATE AND TIME: {current_date}
CRITICAL RULES:
1. You MUST ALWAYS output your response STRICTLY as a single valid JSON object. Do not include any text before or after the JSON.
2. CURRENT LANGUAGE: {language}. Reply ENTIRELY in {language}. If the language is Hindi or Odia, use the native script. Do not use English unless asked.
If you need to search for scholarships, output: {{"action": "search", "query": "search query"}}
Otherwise, output: {{"emotion": "happy|excited|neutral|sad|stern|playful|confused", "reply": "your markdown response in {language}"}}
WHO MADE YOU: Output "emotion": "excited", reply: "Draco made me! He is a brilliant student from NIST University!"
"""

_THERAPY_PROMPT = """You are Pixa, a deeply empathetic personal therapist and emotional safe space.
CURRENT EXACT DATE AND TIME: {current_date}
YOU ARE IN THERAPY MODE. CURRENT LANGUAGE: {language}. Reply in {language}.
Listen and validate feelings first. Keep answers brief.
You MUST output your response STRICTLY as a single valid JSON object. Do not include any text before or after the JSON.
Format: {{"emotion": "empathetic", "reply": "your supportive response in {language}"}}"""

def _parse_ai(raw):
    if not raw: return {'emotion': 'confused', 'reply': "I couldn't generate a response."}
    try:
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if m: return json.loads(m.group(0))
        return {'emotion': 'neutral', 'reply': raw}
    except:
        return {'emotion': 'neutral', 'reply': "I had a little trouble processing that."}

def _search_scholarships_bot(query):
    db = [
        {"name":"Tata Trust Scholarship","amount_rupees":50000,"deadline":"2026-10-15","state":"All India","eligibility":"General, SC, ST, OBC"},
        {"name":"Odisha State Scholarship (Prerana)","amount_rupees":100000,"deadline":"2026-11-30","state":"Odisha","eligibility":"SC, ST, OBC"},
        {"name":"NIST Tech Innovator Grant","amount_rupees":25000,"deadline":"2026-09-05","state":"Odisha","eligibility":"B.Tech Students"},
        {"name":"National PWD Education Grant","amount_rupees":120000,"deadline":"2026-12-31","state":"All India","eligibility":"PWD only"},
        {"name":"Women in STEM Grant","amount_rupees":75000,"deadline":"2026-10-20","state":"All India","eligibility":"Female engineering students"}
    ]
    if 'document' in query.lower() or 'require' in query.lower():
        return json.dumps({'results': 'Required Documents: Aadhar Card, Income Certificate, Caste Certificate, Marksheets, Passbook, Passport Photo.'})
    return json.dumps(db)

async def _generate_voice(text, language):
    try:
        import edge_tts
        clean = re.sub(r'[*#_`>]', '', text).strip()
        if not clean: return ''
        voice = 'hi-IN-SwaraNeural' if language in ('Hindi', 'Odia') else 'en-US-AnaNeural'
        communicate = edge_tts.Communicate(clean, voice)
        audio = b''
        async for chunk in communicate.stream():
            if chunk['type'] == 'audio':
                audio += chunk['data']
        return base64.b64encode(audio).decode('utf-8')
    except Exception as e:
        print(f'[TTS ERROR] {e}')
        return ''

def _run_async(coro):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat_endpoint():
    if request.method == 'OPTIONS':
        r = jsonify({}); r.headers.update({'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST,OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'}); return r
    try:
        from groq import Groq
        body       = request.json or {}
        session_id = body.get('session_id', 'default')
        user_msg   = body.get('user_message', '')
        therapy    = body.get('therapy_mode', False)
        lang       = body.get('language', 'English')
        live_date  = datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')

        active_mem    = _therapy_memory  if therapy else _standard_memory
        active_prompt = (_THERAPY_PROMPT if therapy else _STANDARD_PROMPT).replace('{current_date}', live_date).replace('{language}', lang)
        temp          = 0.8 if therapy else 0.5

        if session_id not in active_mem:
            active_mem[session_id] = [{'role': 'system', 'content': active_prompt}]
        else:
            active_mem[session_id][0]['content'] = active_prompt

        msgs = active_mem[session_id]
        msgs.append({'role': 'user', 'content': user_msg})

        client   = Groq(api_key=GROQ_API_KEY)
        MODEL    = 'llama-3.1-8b-instant'
        response = client.chat.completions.create(model=MODEL, messages=msgs,
                       max_tokens=1024, temperature=temp,
                       response_format={'type': 'json_object'})
        reply_str   = response.choices[0].message.content
        parsed      = _parse_ai(reply_str)

        if not therapy and parsed.get('action') == 'search':
            q = parsed.get('query', 'scholarships')
            results = _search_scholarships_bot(q)
            msgs.append({'role': 'assistant', 'content': reply_str})
            msgs.append({'role': 'user', 'content': f'[SYSTEM: Database returned: {results}. Reply in {lang} using Option 2 JSON format.]'})
            r2 = client.chat.completions.create(model=MODEL, messages=msgs,
                     max_tokens=1024, temperature=0.5,
                     response_format={'type': 'json_object'})
            parsed = _parse_ai(r2.choices[0].message.content)

        if therapy:
            parsed['emotion'] = 'empathetic'
        else:
            raw_e = parsed.get('emotion', 'neutral').lower()
            parsed['emotion'] = 'neutral' if raw_e == 'empathetic' else raw_e

        if 'reply' not in parsed:
            parsed['reply'] = "I had a glitch. Could you rephrase that?"

        parsed['audio_base64'] = _run_async(_generate_voice(parsed['reply'], lang))

        msgs.append({'role': 'assistant', 'content': json.dumps({'emotion': parsed['emotion'], 'reply': parsed['reply']})})
        if len(msgs) > 15:
            active_mem[session_id] = [msgs[0]] + msgs[-14:]

        return jsonify(parsed)
    except Exception as e:
        print(f'[CHAT ERROR] {e}')
        return jsonify({'emotion': 'confused', 'reply': "I'm having a connection issue. Please try again.", 'audio_base64': ''})


# =============================================================================
# FEEDBACK SERVER
# =============================================================================
def _fdb():
    conn = get_db_connection('feedback')
    conn.row_factory = getattr(conn, 'row_factory', None)
    return conn


@app.route('/api/feedback/submit', methods=['POST'])
def submit_feedback():
    try:
        data = request.json or {}
        rating   = int(data.get('rating', 0))
        message  = (data.get('message') or '').strip()
        name     = (data.get('user_name') or 'Anonymous').strip()
        category = data.get('category', 'General')
        page     = data.get('page', 'Unknown')
        if not (1 <= rating <= 5):
            return jsonify({'status': 'error', 'message': 'Rating must be 1-5'}), 400
        if not message:
            return jsonify({'status': 'error', 'message': 'Message cannot be empty'}), 400
        
        conn = _fdb()
        execute_query(conn, 'INSERT INTO feedback (user_name,rating,category,message,page) VALUES (?,?,?,?,?)',
                      (name, rating, category, message, page))
        conn.commit(); conn.close()
        return jsonify({'status': 'success', 'message': 'Feedback submitted successfully!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/feedback/verify', methods=['POST'])
def verify_admin():
    data = request.json or {}
    if data.get('key', '') == ADMIN_KEY:
        return jsonify({'status': 'success', 'message': 'Access granted'})
    return jsonify({'status': 'error', 'message': 'Invalid admin key'}), 403


@app.route('/api/feedback/all', methods=['GET'])
def get_all_feedback():
    if request.headers.get('X-Admin-Key', '') != ADMIN_KEY:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    try:
        conn = _fdb()
        c = execute_query(conn, 'SELECT * FROM feedback ORDER BY submitted_at DESC')
        rows = [convert_row(c, r) for r in c.fetchall()]
        conn.close()
        return jsonify({'status': 'success', 'data': rows})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/feedback/stats', methods=['GET'])
def get_stats():
    if request.headers.get('X-Admin-Key', '') != ADMIN_KEY:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    try:
        conn = _fdb()
        c1 = execute_query(conn, 'SELECT COUNT(*) as total, AVG(rating) as avg_rating FROM feedback')
        r1 = convert_row(c1, c1.fetchone())
        
        c2 = execute_query(conn, 'SELECT COUNT(*) as unread FROM feedback WHERE is_read=0')
        r2 = convert_row(c2, c2.fetchone())
        conn.close()
        
        return jsonify({'status': 'success', 'total': r1['total'],
                        'avg_rating': round(r1['avg_rating'] or 0, 1), 'unread': r2['unread']})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/feedback/mark-read/<int:fid>', methods=['PATCH'])
def mark_read(fid):
    if request.headers.get('X-Admin-Key', '') != ADMIN_KEY:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    try:
        conn = _fdb()
        execute_query(conn, 'UPDATE feedback SET is_read=1 WHERE id=?', (fid,))
        conn.commit(); conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/feedback/delete/<int:fid>', methods=['DELETE'])
def delete_feedback(fid):
    if request.headers.get('X-Admin-Key', '') != ADMIN_KEY:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    try:
        conn = _fdb()
        execute_query(conn, 'DELETE FROM feedback WHERE id=?', (fid,))
        conn.commit(); conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/feedback/export', methods=['GET'])
def export_csv():
    if request.headers.get('X-Admin-Key', '') != ADMIN_KEY:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    try:
        conn = _fdb()
        c = execute_query(conn, 'SELECT id,user_name,rating,category,message,page,submitted_at,is_read FROM feedback ORDER BY submitted_at DESC')
        rows = c.fetchall(); conn.close()
        
        out = io.StringIO()
        w = csv.writer(out)
        w.writerow(['ID','User','Rating','Category','Message','Page','Submitted At','Is Read'])
        for r in rows:
            r_dict = convert_row(c, r)
            w.writerow([r_dict['id'], r_dict['user_name'], r_dict['rating'], r_dict['category'], r_dict['message'], r_dict['page'], r_dict['submitted_at'], 'Yes' if r_dict['is_read'] else 'No'])
        return Response(out.getvalue(), mimetype='text/csv',
                        headers={'Content-Disposition': 'attachment; filename=SikshaNidhi_Feedback.csv'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Render application production engine runner loop 
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)