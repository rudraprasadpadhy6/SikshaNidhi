import os, json, sqlite3, re, base64, asyncio, csv, io
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATA_DIR    = os.path.join(BASE_DIR, 'data')
SCHOLAR_DB  = os.path.join(DATA_DIR, 'scholarships.db')
SCHEMES_DB  = os.path.join(DATA_DIR, 'schemes.db')
FEEDBACK_DB = os.path.join(DATA_DIR, 'feedback.db')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
ADMIN_KEY    = os.getenv('ADMIN_FEEDBACK_KEY', 'siksha-admin-2026')

def _init_feedback():
    conn = sqlite3.connect(FEEDBACK_DB)
    conn.execute('''CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT DEFAULT 'Anonymous',
        rating INTEGER NOT NULL,
        category TEXT DEFAULT 'General',
        message TEXT NOT NULL,
        page TEXT DEFAULT 'Unknown',
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_read INTEGER DEFAULT 0)''')
    conn.commit(); conn.close()

_init_feedback()

# ── Scholar ───────────────────────────────────────────────
def _get_scholarships(payload):
    conn = sqlite3.connect(SCHOLAR_DB); conn.row_factory = sqlite3.Row; c = conn.cursor()
    try: age = int(payload.get('age', 0))
    except: age = 0
    try: marks = int(payload.get('marks', 0))
    except: marks = 0
    try: income = int(payload.get('income', 99999999))
    except: income = 99999999
    gender = payload.get('gender', 'Other')
    caste  = payload.get('caste', 'All')
    pwd    = payload.get('pwd', 'no')
    stype  = payload.get('type')
    q = '''SELECT * FROM scholarships
           WHERE (min_age<=? AND max_age>=?) AND (gender='All' OR gender=?)
             AND (caste='All' OR caste=?) AND min_marks<=? AND max_income>=?'''
    params = [age, age, gender, caste, marks, income]
    if stype: q += ' AND scholarship_type=?'; params.append(stype)
    if pwd.lower() == 'no': q += ' AND pwd_only=False'
    c.execute(q, params); rows = c.fetchall(); conn.close()
    today = datetime.now().strftime('%Y-%m-%d'); out = []
    for r in rows:
        tp = '[Government]' if r['scholarship_type'] == 'Government' else '[Private]'
        st = 'Live' if r['close_date'] >= today else 'Expired'
        info = (f"Scholarship Type: {r['scholarship_type']}\nStart Date: {r['start_date']}\n"
                f"Close Date: {r['close_date']}\nReward Amount: Rs.{r['amount']:,}\n"
                f"Official Website: {r['url']}\n----------------------------------------\nIn Details: {r['description']}")
        out.append({'name': f"{tp} {r['name']} [{st}]", 'amt': r['amount'], 'ds': info,
                    'end': r['close_date'], 'end_date': r['close_date'], 'url': r['url'],
                    'type': r['scholarship_type'], 'status': st, 'docs': r['documents_required']})
    return out

@app.route('/api/search', methods=['POST'])
def search_scholarships():
    try:
        p = request.json
        if not p: return jsonify({'status':'error','message':'No payload'}), 400
        body = json.dumps({'status':'success','data':_get_scholarships(p)}, ensure_ascii=False)
        return Response(body, status=200, mimetype='application/json; charset=utf-8')
    except Exception as e: return jsonify({'status':'error','message':str(e)}), 500

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    try:
        conn = sqlite3.connect(SCHOLAR_DB); conn.row_factory = sqlite3.Row; c = conn.cursor()
        now = datetime.now(); t0 = now.strftime('%Y-%m-%d'); t5 = (now+timedelta(days=5)).strftime('%Y-%m-%d')
        c.execute('SELECT name,close_date,url,documents_required FROM scholarships WHERE close_date>=? AND close_date<=?',(t0,t5))
        rows = c.fetchall(); conn.close()
        out = [{'name':r['name'],'days_left':(datetime.strptime(r['close_date'],'%Y-%m-%d')-now).days+1,
                'url':r['url'],'docs':r['documents_required']} for r in rows]
        return jsonify({'status':'success','notifications':out})
    except Exception as e: return jsonify({'status':'error','message':str(e)}), 500

@app.route('/api/live_scholarships', methods=['GET'])
def get_live():
    try:
        conn = sqlite3.connect(SCHOLAR_DB); conn.row_factory = sqlite3.Row; c = conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        c.execute('SELECT name,close_date,url,amount,scholarship_type,documents_required FROM scholarships WHERE close_date>=? ORDER BY close_date ASC LIMIT 10',(today,))
        rows = c.fetchall(); conn.close()
        return jsonify({'status':'success','data':[{'name':r['name'],'close_date':r['close_date'],
            'url':r['url'],'amt':r['amount'],'type':r['scholarship_type'],'status':'Ongoing',
            'docs':r['documents_required']} for r in rows]})
    except Exception as e: return jsonify({'status':'error','message':str(e)}), 500

# ── Capital ───────────────────────────────────────────────
def _scheme_html(s):
    sid = s['id']
    return f'''<span style="cursor:pointer;color:#054c5a;text-decoration:underline;display:block;padding:5px 0;"
      onclick="const t=document.getElementById('details-{sid}').innerHTML;const c=document.getElementById('success-screen');if(!window.originalListCache)window.originalListCache=c.innerHTML;c.innerHTML=t;">
  {s['name']} <small style="color:#4dcbc6;font-size:14px;margin-left:10px;">(Click for details)</small>
</span>
<template id="details-{sid}">
  <div style="text-align:left;padding:10px;font-family:'Segoe UI',sans-serif;">
    <h2 style="color:#0b5b6a;font-size:34px;">{s['name']}</h2>
    <p style="color:#666;font-size:20px;">{s['description']}</p>
    <div style="background:#e8f8f9;padding:25px;border-radius:12px;margin-bottom:25px;">
      <h3 style="color:#0b5b6a;font-size:22px;">About This Opportunity</h3>
      <p style="color:#444;font-size:18px;line-height:1.6;">{s['long_description']}</p>
    </div>
    <div style="background:#e8f8f9;padding:25px;border-radius:12px;margin-bottom:40px;">
      <h3 style="color:#0b5b6a;font-size:22px;">Why We Chose This For You</h3>
      <p style="color:#444;font-size:18px;line-height:1.6;">{s['why_chosen']}</p>
    </div>
    <div style="display:flex;gap:20px;">
      <button onclick="document.getElementById('success-screen').innerHTML=window.originalListCache;window.originalListCache=null;"
        style="background:#e8f8f9;color:#4dcbc6;padding:20px 30px;font-size:22px;font-weight:600;border:none;border-radius:12px;cursor:pointer;flex:1;">Back to List</button>
      <a href="{s['official_website']}" target="_blank"
        style="background:#4dcbc6;color:white;padding:20px 30px;font-size:22px;font-weight:600;border-radius:12px;text-decoration:none;text-align:center;flex:1;display:inline-block;">Official Website</a>
    </div>
  </div>
</template>'''

@app.route('/api/find-opportunities', methods=['POST','OPTIONS'])
def find_opportunities():
    if request.method == 'OPTIONS':
        r = jsonify({}); r.headers.update({'Access-Control-Allow-Origin':'*','Access-Control-Allow-Methods':'POST,OPTIONS','Access-Control-Allow-Headers':'Content-Type'}); return r
    try:
        data = request.json or {}
        age = int(data.get('age',0)); state = data.get('state',''); marital = data.get('maritalStatus','')
        category = data.get('category',''); disability = data.get('disability','No')=='Yes'
        education = data.get('education',''); employment = data.get('employment','')
        conn = sqlite3.connect(SCHEMES_DB); cur = conn.cursor()
        cur.execute('SELECT * FROM financial_schemes')
        cols = [c[0] for c in cur.description]; rows = cur.fetchall(); conn.close()
        eligible = []
        for row in rows:
            s = dict(zip(cols,row))
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
            eligible.append({'name':_scheme_html(s),'description':s['description'],
                'official_website':s['official_website'],'priority':s['priority'],
                'docs':s.get('documents_required','1. Aadhar Card\n2. Income Certificate\n3. Bank Passbook')})
        eligible.sort(key=lambda x:x['priority'],reverse=True)
        return jsonify({'success':True,'count':len(eligible),'opportunities':eligible})
    except Exception as e: return jsonify({'error':str(e)}), 500

@app.route('/api/add-opportunity', methods=['POST','OPTIONS'])
def add_opportunity():
    if request.method=='OPTIONS':
        r=jsonify({}); r.headers.update({'Access-Control-Allow-Origin':'*','Access-Control-Allow-Methods':'POST,OPTIONS','Access-Control-Allow-Headers':'Content-Type'}); return r
    try:
        data = request.json or {}
        conn = sqlite3.connect(SCHEMES_DB); cur = conn.cursor()
        cur.execute('''INSERT INTO financial_schemes (name,description,long_description,why_chosen,official_website,
            target_states,min_age,max_age,marital_status,categories,disability_required,education_levels,employment_statuses,priority)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
            (data.get('name','Untitled'),data.get('description',''),data.get('long_description',''),
             data.get('why_chosen',''),data.get('official_website',''),json.dumps(data.get('target_states',['ALL'])),
             data.get('min_age'),data.get('max_age'),json.dumps(data.get('marital_status',[])),
             json.dumps(data.get('categories',[])),data.get('disability_required',False),
             json.dumps(data.get('education_levels',[])),json.dumps(data.get('employment_statuses',[])),data.get('priority',5)))
        conn.commit(); new_id = cur.lastrowid; conn.close()
        return jsonify({'success':True,'id':new_id,'message':'Added successfully'}), 201
    except Exception as e: return jsonify({'error':str(e)}), 500

# ── PixaBot ───────────────────────────────────────────────
_smem = {}; _tmem = {}
_SP = ("You are Pixa, educational advisor for ShikshaNidhi.\nDATE: {d}\nCURRENT LANGUAGE: {l}. Reply in {l}.\n"
       "Output STRICTLY as JSON:\nOPTION1: {{\"action\":\"search\",\"query\":\"...\"}}\n"
       "OPTION2: {{\"emotion\":\"happy|excited|neutral|sad|stern|playful|confused\",\"reply\":\"...\"}}")
_TP = ("You are Pixa, empathetic therapist.\nDATE: {d}\nTHERAPY MODE. Language: {l}. Reply in {l}.\n"
       "Output STRICTLY as JSON: {{\"emotion\":\"empathetic\",\"reply\":\"...\"}}")

def _parse(raw):
    if not raw: return {'emotion':'confused','reply':"I couldn't generate a response."}
    try:
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        return json.loads(m.group(0)) if m else {'emotion':'neutral','reply':raw}
    except: return {'emotion':'neutral','reply':"I had trouble processing that."}

def _bot_search(q):
    db=[{"name":"Tata Trust Scholarship","amount_rupees":50000,"deadline":"2026-10-15"},
        {"name":"Odisha State Scholarship","amount_rupees":100000,"deadline":"2026-11-30"},
        {"name":"National PWD Education Grant","amount_rupees":120000,"deadline":"2026-12-31"},
        {"name":"Women in STEM Grant","amount_rupees":75000,"deadline":"2026-10-20"}]
    if 'document' in q.lower(): return json.dumps({'results':'Aadhar Card, Income Certificate, Caste Certificate, Marksheets, Passbook, Photo.'})
    return json.dumps(db)

async def _voice(text, lang):
    try:
        import edge_tts
        clean = re.sub(r'[*#_`>]','',text).strip()
        if not clean: return ''
        voice = 'hi-IN-SwaraNeural' if lang in ('Hindi','Odia') else 'en-US-AnaNeural'
        comm = edge_tts.Communicate(clean, voice); audio = b''
        async for chunk in comm.stream():
            if chunk['type']=='audio': audio += chunk['data']
        return base64.b64encode(audio).decode('utf-8')
    except: return ''

def _run(coro):
    loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
    try: return loop.run_until_complete(coro)
    finally: loop.close()

@app.route('/api/chat', methods=['POST','OPTIONS'])
def chat():
    if request.method=='OPTIONS':
        r=jsonify({}); r.headers.update({'Access-Control-Allow-Origin':'*','Access-Control-Allow-Methods':'POST,OPTIONS','Access-Control-Allow-Headers':'Content-Type'}); return r
    try:
        from groq import Groq
        body = request.json or {}
        sid = body.get('session_id','default'); msg = body.get('user_message','')
        therapy = body.get('therapy_mode',False); lang = body.get('language','English')
        dt = datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')
        mem = _tmem if therapy else _smem
        prompt = (_TP if therapy else _SP).format(d=dt, l=lang)
        temp = 0.8 if therapy else 0.5
        if sid not in mem: mem[sid] = [{'role':'system','content':prompt}]
        else: mem[sid][0]['content'] = prompt
        msgs = mem[sid]; msgs.append({'role':'user','content':msg})
        client = Groq(api_key=GROQ_API_KEY); MODEL='llama-3.1-8b-instant'
        resp = client.chat.completions.create(model=MODEL,messages=msgs,max_tokens=1024,temperature=temp,response_format={'type':'json_object'})
        raw = resp.choices[0].message.content; parsed = _parse(raw)
        if not therapy and parsed.get('action')=='search':
            res = _bot_search(parsed.get('query',''))
            msgs.append({'role':'assistant','content':raw})
            msgs.append({'role':'user','content':f'[SYSTEM: DB returned: {res}. Reply in {lang} using Option2 JSON.]'})
            r2 = client.chat.completions.create(model=MODEL,messages=msgs,max_tokens=1024,temperature=0.5,response_format={'type':'json_object'})
            parsed = _parse(r2.choices[0].message.content)
        if therapy: parsed['emotion']='empathetic'
        else:
            e = parsed.get('emotion','neutral').lower()
            parsed['emotion'] = 'neutral' if e=='empathetic' else e
        if 'reply' not in parsed: parsed['reply']="I had a glitch. Could you rephrase that?"
        parsed['audio_base64'] = _run(_voice(parsed['reply'], lang))
        msgs.append({'role':'assistant','content':json.dumps({'emotion':parsed['emotion'],'reply':parsed['reply']})})
        if len(msgs)>15: mem[sid]=[msgs[0]]+msgs[-14:]
        return jsonify(parsed)
    except Exception as e:
        print(f'[CHAT ERROR] {e}')
        return jsonify({'emotion':'confused','reply':"Connection issue. Please try again.",'audio_base64':''})

# ── Feedback ──────────────────────────────────────────────
def _fdb(): conn=sqlite3.connect(FEEDBACK_DB); conn.row_factory=sqlite3.Row; return conn

@app.route('/api/feedback/submit', methods=['POST'])
def submit_feedback():
    try:
        data=request.json or {}; rating=int(data.get('rating',0))
        msg=(data.get('message') or '').strip(); name=(data.get('user_name') or 'Anonymous').strip()
        if not (1<=rating<=5): return jsonify({'status':'error','message':'Rating must be 1-5'}),400
        if not msg: return jsonify({'status':'error','message':'Message cannot be empty'}),400
        conn=_fdb(); conn.execute('INSERT INTO feedback (user_name,rating,category,message,page) VALUES (?,?,?,?,?)',
            (name,rating,data.get('category','General'),msg,data.get('page','Unknown')))
        conn.commit(); conn.close()
        return jsonify({'status':'success','message':'Feedback submitted!'})
    except Exception as e: return jsonify({'status':'error','message':str(e)}),500

@app.route('/api/feedback/verify', methods=['POST'])
def verify_admin():
    data=request.json or {}
    if data.get('key','')==ADMIN_KEY: return jsonify({'status':'success','message':'Access granted'})
    return jsonify({'status':'error','message':'Invalid admin key'}),403

@app.route('/api/feedback/all', methods=['GET'])
def get_all_feedback():
    if request.headers.get('X-Admin-Key','')==ADMIN_KEY:
        conn=_fdb(); c=conn.cursor(); c.execute('SELECT * FROM feedback ORDER BY submitted_at DESC')
        rows=[dict(r) for r in c.fetchall()]; conn.close()
        return jsonify({'status':'success','data':rows})
    return jsonify({'status':'error','message':'Unauthorized'}),403

@app.route('/api/feedback/stats', methods=['GET'])
def get_stats():
    if request.headers.get('X-Admin-Key','')==ADMIN_KEY:
        conn=_fdb(); c=conn.cursor()
        c.execute('SELECT COUNT(*) as total,AVG(rating) as avg FROM feedback'); row=c.fetchone()
        c.execute('SELECT COUNT(*) as u FROM feedback WHERE is_read=0'); ur=c.fetchone(); conn.close()
        return jsonify({'status':'success','total':row['total'],'avg_rating':round(row['avg'] or 0,1),'unread':ur['u']})
    return jsonify({'status':'error','message':'Unauthorized'}),403

@app.route('/api/feedback/mark-read/<int:fid>', methods=['PATCH'])
def mark_read(fid):
    if request.headers.get('X-Admin-Key','')==ADMIN_KEY:
        conn=_fdb(); conn.execute('UPDATE feedback SET is_read=1 WHERE id=?',(fid,)); conn.commit(); conn.close()
        return jsonify({'status':'success'})
    return jsonify({'status':'error','message':'Unauthorized'}),403

@app.route('/api/feedback/delete/<int:fid>', methods=['DELETE'])
def delete_feedback(fid):
    if request.headers.get('X-Admin-Key','')==ADMIN_KEY:
        conn=_fdb(); conn.execute('DELETE FROM feedback WHERE id=?',(fid,)); conn.commit(); conn.close()
        return jsonify({'status':'success'})
    return jsonify({'status':'error','message':'Unauthorized'}),403

@app.route('/api/feedback/export', methods=['GET'])
def export_csv():
    if request.headers.get('X-Admin-Key','')==ADMIN_KEY:
        conn=_fdb(); c=conn.cursor()
        c.execute('SELECT id,user_name,rating,category,message,page,submitted_at,is_read FROM feedback ORDER BY submitted_at DESC')
        rows=c.fetchall(); conn.close(); out=io.StringIO(); w=csv.writer(out)
        w.writerow(['ID','User','Rating','Category','Message','Page','Submitted At','Is Read'])
        for r in rows: w.writerow([r['id'],r['user_name'],r['rating'],r['category'],r['message'],r['page'],r['submitted_at'],'Yes' if r['is_read'] else 'No'])
        return Response(out.getvalue(),mimetype='text/csv',headers={'Content-Disposition':'attachment; filename=SikshaNidhi_Feedback.csv'})
    return jsonify({'status':'error','message':'Unauthorized'}),403

@app.route('/health', methods=['GET'])
def health(): return jsonify({'status':'ok','message':'SikshaNidhi Backend Running'})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
