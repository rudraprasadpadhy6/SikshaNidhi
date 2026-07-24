import os, json, re, base64, asyncio, csv, io
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
ADMIN_KEY    = os.getenv('ADMIN_FEEDBACK_KEY', 'siksha-admin-2026')

# ── IN-MEMORY DATA STORES ──────────────────────────────────
SCHOLARSHIPS_DATA = [
    {
        'id': 1,
        'name': 'Post Matric Scholarship for SC',
        'scholarship_type': 'Government',
        'amount': 25000,
        'description': 'Financial assistance to SC students for post-matriculation studies.',
        'start_date': '2024-01-01',
        'close_date': '2026-12-31',
        'url': 'https://scholarships.gov.in',
        'min_age': 10,
        'max_age': 35,
        'gender': 'All',
        'caste': 'SC',
        'pwd_only': False,
        'min_marks': 50,
        'max_income': 250000,
        'documents_required': '1. Aadhar Card\n2. Income Certificate\n3. Caste Certificate\n4. Marksheet\n5. Bank Passbook'
    },
    {
        'id': 2,
        'name': 'Pragati Scholarship for Girls',
        'scholarship_type': 'Government',
        'amount': 50000,
        'description': 'AICTE scheme to provide encouragement and support to girl children.',
        'start_date': '2024-05-01',
        'close_date': '2026-12-31',
        'url': 'https://aicte-india.org',
        'min_age': 17,
        'max_age': 25,
        'gender': 'Female',
        'caste': 'All',
        'pwd_only': False,
        'min_marks': 60,
        'max_income': 800000,
        'documents_required': '1. Aadhar Card\n2. Income Certificate\n3. Marksheet\n4. Admission Letter'
    },
    {
        'id': 3,
        'name': 'National Merit-cum-Means Scholarship',
        'scholarship_type': 'Government',
        'amount': 12000,
        'description': 'For meritorious students of economically weaker sections.',
        'start_date': '2025-01-01',
        'close_date': '2027-01-31',
        'url': 'https://scholarships.gov.in',
        'min_age': 10,
        'max_age': 18,
        'gender': 'All',
        'caste': 'All',
        'pwd_only': False,
        'min_marks': 55,
        'max_income': 350000,
        'documents_required': '1. Aadhar Card\n2. Income Certificate\n3. Marksheet'
    },
    {
        'id': 4,
        'name': 'KVPY Fellowship',
        'scholarship_type': 'Government',
        'amount': 84000,
        'description': 'Scholarship program to encourage students to take up research careers in Basic Sciences.',
        'start_date': '2024-06-01',
        'close_date': '2025-12-31',
        'url': 'http://kvpy.iisc.ac.in',
        'min_age': 15,
        'max_age': 20,
        'gender': 'All',
        'caste': 'All',
        'pwd_only': False,
        'min_marks': 75,
        'max_income': 1000000,
        'documents_required': '1. Aadhar Card\n2. Academic Records\n3. Institution ID'
    },
    {
        'id': 5,
        'name': 'Pre-Matric Minority Scholarship',
        'scholarship_type': 'Government',
        'amount': 10000,
        'description': 'Financial assistance for minority community students.',
        'start_date': '2023-01-01',
        'close_date': '2023-12-31',
        'url': 'https://scholarships.gov.in',
        'min_age': 10,
        'max_age': 16,
        'gender': 'All',
        'caste': 'Minority',
        'pwd_only': False,
        'min_marks': 50,
        'max_income': 200000,
        'documents_required': '1. Aadhar Card\n2. Minority Certificate'
    },
    {
        'id': 6,
        'name': 'Tata Trust Medical/Engineering',
        'scholarship_type': 'Private',
        'amount': 60000,
        'description': 'Merit-based scholarship for undergrad students in top institutions.',
        'start_date': '2024-07-01',
        'close_date': '2026-08-31',
        'url': 'https://www.tatatrusts.org',
        'min_age': 17,
        'max_age': 25,
        'gender': 'All',
        'caste': 'All',
        'pwd_only': False,
        'min_marks': 85,
        'max_income': 1200000,
        'documents_required': '1. Aadhar Card\n2. College ID\n3. Marksheet\n4. Fee Receipt'
    },
    {
        'id': 7,
        'name': 'Reliance Foundation Scholarship',
        'scholarship_type': 'Private',
        'amount': 200000,
        'description': 'Supporting India’s brightest youth to fulfill their potential.',
        'start_date': '2025-02-01',
        'close_date': '2027-01-31',
        'url': 'https://www.reliancefoundation.org',
        'min_age': 18,
        'max_age': 30,
        'gender': 'All',
        'caste': 'All',
        'pwd_only': False,
        'min_marks': 80,
        'max_income': 1500000,
        'documents_required': '1. Aadhar Card\n2. Income Proof\n3. Academic Records'
    },
    {
        'id': 8,
        'name': 'Loreal Paris Women in Science',
        'scholarship_type': 'Private',
        'amount': 250000,
        'description': 'Empowering young women pursuing careers in science and STEM fields.',
        'start_date': '2024-02-15',
        'close_date': '2026-11-30',
        'url': 'https://www.loreal.com',
        'min_age': 17,
        'max_age': 25,
        'gender': 'Female',
        'caste': 'All',
        'pwd_only': False,
        'min_marks': 85,
        'max_income': 600000,
        'documents_required': '1. Aadhar Card\n2. Admission Proof\n3. 12th Marksheet'
    },
    {
        'id': 9,
        'name': 'Special Ability Tech Grant',
        'scholarship_type': 'Private',
        'amount': 75000,
        'description': 'Grant for students with benchmark disabilities pursuing technology.',
        'start_date': '2025-01-01',
        'close_date': '2026-12-31',
        'url': 'https://pwd-grants.org',
        'min_age': 15,
        'max_age': 35,
        'gender': 'All',
        'caste': 'All',
        'pwd_only': True,
        'min_marks': 50,
        'max_income': 1500000,
        'documents_required': '1. UDID Certificate\n2. Aadhar Card\n3. College Enrollment Proof'
    },
    {
        'id': 10,
        'name': 'HDFC Badhte Kadam Scholarship',
        'scholarship_type': 'Private',
        'amount': 100000,
        'description': 'Supports students who have faced hard times to continue education.',
        'start_date': '2023-05-01',
        'close_date': '2024-03-31',
        'url': 'https://hdfcbank.com',
        'min_age': 18,
        'max_age': 28,
        'gender': 'All',
        'caste': 'All',
        'pwd_only': False,
        'min_marks': 60,
        'max_income': 600000,
        'documents_required': '1. Aadhar Card\n2. Income Proof\n3. Marksheets'
    }
]

FINANCIAL_SCHEMES_DATA = [
    {
        'id': 1,
        'name': 'Post Matric Scholarship for Minorities',
        'description': 'Scholarship for students belonging to minority communities to pursue higher education.',
        'long_description': 'A flagship program providing regular financial assistance to students from minority communities across the nation to support their higher education goals.',
        'why_chosen': "Based on your 'Minority' category and 'Student' status, this scheme ensures monetary support for your studies.",
        'official_website': 'https://scholarships.gov.in/',
        'target_states': ['ALL'],
        'min_age': 15,
        'max_age': 35,
        'marital_status': [],
        'categories': ['Minority'],
        'disability_required': False,
        'education_levels': ['10th Pass', '12th Pass', 'Graduate', 'Postgraduate'],
        'employment_statuses': ['Student'],
        'priority': 10,
        'documents_required': '1. Aadhar Card\n2. Income Certificate\n3. Caste/Minority Certificate\n4. Previous Year Marksheet\n5. Bank Passbook'
    },
    {
        'id': 2,
        'name': 'Indira Gandhi National Widow Pension Scheme',
        'description': 'Provides monthly pension to widows living below poverty line.',
        'long_description': 'A flagship program under the National Social Assistance Programme (NSAP) providing regular, fixed-amount non-contributory pensions to eligible widowed women across the nation.',
        'why_chosen': "Based on your 'Widowed' marital status, this scheme ensures a steady flow of foundational monetary support guaranteed by the central government.",
        'official_website': 'https://nsap.nic.in/',
        'target_states': ['ALL'],
        'min_age': 40,
        'max_age': 100,
        'marital_status': ['Widow'],
        'categories': [],
        'disability_required': False,
        'education_levels': [],
        'employment_statuses': [],
        'priority': 8,
        'documents_required': '1. Aadhar Card\n2. Death Certificate of Husband\n3. BPL Card\n4. Age Proof\n5. Bank Passbook'
    },
    {
        'id': 3,
        'name': 'Deendayal Disabled Rehabilitation Scheme',
        'description': 'Financial assistance to provide equal opportunities, equity, and social justice to persons with disabilities.',
        'long_description': 'A comprehensive scheme providing grant-in-aid to NGOs for various projects for rehabilitation of persons with disabilities, ensuring their equal participation.',
        'why_chosen': "Based on your 'Disability' status, this program guarantees specialized support and rehabilitation services.",
        'official_website': 'https://disabilityaffairs.gov.in/',
        'target_states': ['ALL'],
        'min_age': 0,
        'max_age': 100,
        'marital_status': [],
        'categories': [],
        'disability_required': True,
        'education_levels': [],
        'employment_statuses': [],
        'priority': 9,
        'documents_required': '1. Disability Certificate (UDID)\n2. Aadhar Card\n3. Income Certificate\n4. Passport Size Photo'
    },
    {
        'id': 4,
        'name': 'Stand Up India Scheme',
        'description': 'Facilitates bank loans between ₹10 lakh and ₹1 crore to SC, ST, and women borrowers.',
        'long_description': 'A government initiative specifically targeting grassroots entrepreneurship to facilitate bank loans for setting up a greenfield enterprise in manufacturing, services or trading sectors.',
        'why_chosen': 'Based on your background and employment status, this initiative can fund your entrepreneurial goals.',
        'official_website': 'https://www.standupmitra.in/',
        'target_states': ['ALL'],
        'min_age': 18,
        'max_age': 100,
        'marital_status': [],
        'categories': ['SC', 'ST'],
        'disability_required': False,
        'education_levels': [],
        'employment_statuses': ['Self-Employed', 'Working', 'Unemployed'],
        'priority': 7,
        'documents_required': '1. Identity Proof (Aadhar/PAN)\n2. Caste Certificate (if SC/ST)\n3. Project Report\n4. Bank Statements'
    },
    {
        'id': 5,
        'name': 'PM-SVANidhi',
        'description': 'Special Micro-Credit Facility for Street Vendors to resume their livelihoods.',
        'long_description': 'A central sector scheme to facilitate working capital loans up to ₹10,000 for street vendors, completely backed by the government.',
        'why_chosen': 'Given your Self-Employed status, this provides immediate micro-credit access to support your livelihood.',
        'official_website': 'https://pmsvanidhi.mohua.gov.in/',
        'target_states': ['ALL'],
        'min_age': 18,
        'max_age': 100,
        'marital_status': [],
        'categories': [],
        'disability_required': False,
        'education_levels': [],
        'employment_statuses': ['Self-Employed'],
        'priority': 6,
        'documents_required': '1. Vending Certificate / ID Card issued by ULB\n2. Aadhar Card linked to Mobile\n3. Bank Account details'
    },
    {
        'id': 6,
        'name': 'National Fellowship for OBC Students',
        'description': 'Financial assistance to OBC students for pursuing M.Phil and Ph.D.',
        'long_description': 'A fellowship scheme designed to increase opportunities for higher education (M.Phil/Ph.D) among the OBC community with monthly stipends.',
        'why_chosen': "Based on your 'OBC' category and 'Postgraduate' level, this fellowship offers guaranteed stipends for research.",
        'official_website': 'https://socialjustice.gov.in/',
        'target_states': ['ALL'],
        'min_age': 20,
        'max_age': 40,
        'marital_status': [],
        'categories': ['OBC'],
        'disability_required': False,
        'education_levels': ['Postgraduate'],
        'employment_statuses': ['Student'],
        'priority': 9,
        'documents_required': '1. Caste Certificate (OBC Non-Creamy Layer)\n2. Post-Graduation Marksheet\n3. Admission Proof for M.Phil/Ph.D\n4. Aadhar Card'
    },
    {
        'id': 7,
        'name': 'Pradhan Mantri Kaushal Vikas Yojana (PMKVY)',
        'description': 'Skill development initiative scheme to encourage youth for skill training.',
        'long_description': 'The flagship scheme of the Ministry of Skill Development & Entrepreneurship implemented by NSDC to enable youths to take up industry-relevant skill training.',
        'why_chosen': 'This program directly matches your need for training and certification to boost employment prospects.',
        'official_website': 'https://www.pmkvyofficial.org/',
        'target_states': ['ALL'],
        'min_age': 15,
        'max_age': 45,
        'marital_status': [],
        'categories': [],
        'disability_required': False,
        'education_levels': ['No Schooling', '10th Pass', '12th Pass'],
        'employment_statuses': ['Unemployed', 'Student'],
        'priority': 8,
        'documents_required': '1. Aadhar Card\n2. Passport Size Color Photograph\n3. Educational certificates (if any)'
    }
]

FEEDBACK_DATA = []
feedback_id_counter = 1

# ── SCHOLAR ───────────────────────────────────────────────
def _get_scholarships(payload):
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
    
    today = datetime.now().strftime('%Y-%m-%d')
    out = []
    
    for r in SCHOLARSHIPS_DATA:
        if r['min_age'] > age or r['max_age'] < age: continue
        if r['gender'] != 'All' and r['gender'] != gender: continue
        if r['caste'] != 'All' and r['caste'] != caste: continue
        if r['min_marks'] > marks: continue
        if r['max_income'] < income: continue
        if stype and r['scholarship_type'] != stype: continue
        if pwd.lower() == 'no' and r['pwd_only']: continue
        
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
        now = datetime.now(); t0 = now.strftime('%Y-%m-%d'); t5 = (now+timedelta(days=5)).strftime('%Y-%m-%d')
        out = []
        for r in SCHOLARSHIPS_DATA:
            if t0 <= r['close_date'] <= t5:
                close_dt = datetime.strptime(r['close_date'], '%Y-%m-%d')
                days_left = (close_dt - now).days + 1
                out.append({'name': r['name'], 'days_left': days_left, 'url': r['url'], 'docs': r['documents_required']})
        return jsonify({'status':'success','notifications':out})
    except Exception as e: return jsonify({'status':'error','message':str(e)}), 500

@app.route('/api/live_scholarships', methods=['GET'])
def get_live():
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        active = [r for r in SCHOLARSHIPS_DATA if r['close_date'] >= today]
        active.sort(key=lambda r: r['close_date'])
        out = [{'name':r['name'],'close_date':r['close_date'],
                'url':r['url'],'amt':r['amount'],'type':r['scholarship_type'],'status':'Ongoing',
                'docs':r['documents_required']} for r in active[:10]]
        return jsonify({'status':'success','data':out})
    except Exception as e: return jsonify({'status':'error','message':str(e)}), 500

# ── CAPITAL ───────────────────────────────────────────────
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
        eligible = []
        for s in FINANCIAL_SCHEMES_DATA:
            if s.get('min_age') is not None and age < s['min_age']: continue
            if s.get('max_age') is not None and age > s['max_age']: continue
            ts = s.get('target_states', ['ALL'])
            if 'ALL' not in ts and state not in ts: continue
            vms = s.get('marital_status', [])
            if vms and marital not in vms: continue
            vc = s.get('categories', [])
            if vc and category not in vc: continue
            if s.get('disability_required') and not disability: continue
            ve = s.get('education_levels', [])
            if ve and education not in ve: continue
            vemp = s.get('employment_statuses', [])
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
        new_id = len(FINANCIAL_SCHEMES_DATA) + 1
        new_scheme = {
            'id': new_id,
            'name': data.get('name', 'Untitled'),
            'description': data.get('description', ''),
            'long_description': data.get('long_description', ''),
            'why_chosen': data.get('why_chosen', ''),
            'official_website': data.get('official_website', ''),
            'target_states': data.get('target_states', ['ALL']),
            'min_age': data.get('min_age'),
            'max_age': data.get('max_age'),
            'marital_status': data.get('marital_status', []),
            'categories': data.get('categories', []),
            'disability_required': data.get('disability_required', False),
            'education_levels': data.get('education_levels', []),
            'employment_statuses': data.get('employment_statuses', []),
            'priority': data.get('priority', 5),
            'documents_required': data.get('documents_required', '1. Aadhar Card\n2. Income Certificate\n3. Bank Passbook')
        }
        FINANCIAL_SCHEMES_DATA.append(new_scheme)
        return jsonify({'success':True,'id':new_id,'message':'Added successfully'}), 201
    except Exception as e: return jsonify({'error':str(e)}), 500

# ── PIXABOT ───────────────────────────────────────────────
_smem = {}; _tmem = {}
_SP = ("You are Pixa, an interactive educational advisor for the ShikshaNidhi app.\n"
       "DATE: {d}\n"
       "CURRENT LANGUAGE: {l}. Reply in {l}.\n"
       "You MUST output your response STRICTLY as a single valid JSON object. Do not include any text before or after the JSON. "
       "If you need to search for scholarships, output: {{\"action\":\"search\",\"query\":\"search query\"}}. "
       "Otherwise, output: {{\"emotion\":\"happy|excited|neutral|sad|stern|playful|confused\",\"reply\":\"your response in {l}\"}}")
_TP = ("You are Pixa, a deeply empathetic personal therapist and emotional safe space.\n"
       "DATE: {d}\n"
       "THERAPY MODE. Language: {l}. Reply in {l}.\n"
       "You MUST output your response STRICTLY as a single valid JSON object. Do not include any text before or after the JSON. "
       "Format: {{\"emotion\":\"empathetic\",\"reply\":\"your supportive response in {l}\"}}")

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

# ── FEEDBACK ──────────────────────────────────────────────
@app.route('/api/feedback/submit', methods=['POST'])
def submit_feedback():
    global feedback_id_counter
    try:
        data=request.json or {}; rating=int(data.get('rating',0))
        msg=(data.get('message') or '').strip(); name=(data.get('user_name') or 'Anonymous').strip()
        if not (1<=rating<=5): return jsonify({'status':'error','message':'Rating must be 1-5'}),400
        if not msg: return jsonify({'status':'error','message':'Message cannot be empty'}),400
        
        entry = {
            'id': feedback_id_counter,
            'user_name': name,
            'rating': rating,
            'category': data.get('category', 'General'),
            'message': msg,
            'page': data.get('page', 'Unknown'),
            'submitted_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'is_read': 0
        }
        feedback_id_counter += 1
        FEEDBACK_DATA.append(entry)
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
        rows = sorted(FEEDBACK_DATA, key=lambda x: x['submitted_at'], reverse=True)
        return jsonify({'status':'success','data':rows})
    return jsonify({'status':'error','message':'Unauthorized'}),403

@app.route('/api/feedback/stats', methods=['GET'])
def get_stats():
    if request.headers.get('X-Admin-Key','')==ADMIN_KEY:
        total = len(FEEDBACK_DATA)
        avg = (sum(r['rating'] for r in FEEDBACK_DATA) / total) if total > 0 else 0
        unread = sum(1 for r in FEEDBACK_DATA if r['is_read'] == 0)
        return jsonify({'status':'success','total':total,'avg_rating':round(avg,1),'unread':unread})
    return jsonify({'status':'error','message':'Unauthorized'}),403

@app.route('/api/feedback/mark-read/<int:fid>', methods=['PATCH'])
def mark_read(fid):
    if request.headers.get('X-Admin-Key','')==ADMIN_KEY:
        for r in FEEDBACK_DATA:
            if r['id'] == fid:
                r['is_read'] = 1
                break
        return jsonify({'status':'success'})
    return jsonify({'status':'error','message':'Unauthorized'}),403

@app.route('/api/feedback/delete/<int:fid>', methods=['DELETE'])
def delete_feedback(fid):
    global FEEDBACK_DATA
    if request.headers.get('X-Admin-Key','')==ADMIN_KEY:
        FEEDBACK_DATA = [r for r in FEEDBACK_DATA if r['id'] != fid]
        return jsonify({'status':'success'})
    return jsonify({'status':'error','message':'Unauthorized'}),403

@app.route('/api/feedback/export', methods=['GET'])
def export_csv():
    if request.headers.get('X-Admin-Key','')==ADMIN_KEY:
        rows = sorted(FEEDBACK_DATA, key=lambda x: x['submitted_at'], reverse=True)
        out=io.StringIO(); w=csv.writer(out)
        w.writerow(['ID','User','Rating','Category','Message','Page','Submitted At','Is Read'])
        for r in rows: w.writerow([r['id'],r['user_name'],r['rating'],r['category'],r['message'],r['page'],r['submitted_at'],'Yes' if r['is_read'] else 'No'])
        return Response(out.getvalue(),mimetype='text/csv',headers={'Content-Disposition':'attachment; filename=SikshaNidhi_Feedback.csv'})
    return jsonify({'status':'error','message':'Unauthorized'}),403

@app.route('/health', methods=['GET'])
def health(): return jsonify({'status':'ok','message':'SikshaNidhi In-Memory Engine Running'})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
