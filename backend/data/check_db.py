import sqlite3
from datetime import datetime

today = datetime.now().strftime('%Y-%m-%d')
print('Today:', today)
print()

db = r'backend\data\scholarships.db'
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
c = conn.cursor()
c.execute('SELECT name, scholarship_type, close_date, gender, caste, min_age, max_age, min_marks, max_income, pwd_only FROM scholarships ORDER BY close_date')
rows = c.fetchall()
conn.close()

print(f'=== SCHOLARSHIPS ({len(rows)} total) ===')
for r in rows:
    status = 'LIVE' if r['close_date'] >= today else 'EXPIRED'
    name = r['name']
    stype = r['scholarship_type']
    cd = r['close_date']
    gender = r['gender']
    caste = r['caste']
    minage = r['min_age']
    maxage = r['max_age']
    marks = r['min_marks']
    income = r['max_income']
    pwd = r['pwd_only']
    print(f'[{status}] {name}')
    print(f'  Type:{stype} | Close:{cd} | Gender:{gender} | Caste:{caste}')
    print(f'  Age:{minage}-{maxage} | Marks>={marks} | Income<={income} | PWD:{pwd}')

print()
db2 = r'backend\data\schemes.db'
conn2 = sqlite3.connect(db2)
conn2.row_factory = sqlite3.Row
c2 = conn2.cursor()
c2.execute('SELECT id, name, target_states, marital_status, categories, education_levels, employment_statuses, min_age, max_age, disability_required FROM financial_schemes')
rows2 = c2.fetchall()
conn2.close()

print(f'=== SCHEMES ({len(rows2)} total) ===')
for r in rows2:
    name = r['name']
    states = r['target_states']
    marital = r['marital_status']
    cats = r['categories']
    edu = r['education_levels']
    emp = r['employment_statuses']
    minage = r['min_age']
    maxage = r['max_age']
    dis = r['disability_required']
    print(f'  {name}')
    print(f'  States:{states} | Marital:{marital} | Categories:{cats}')
    print(f'  Education:{edu} | Employment:{emp} | Age:{minage}-{maxage} | Disability:{dis}')
