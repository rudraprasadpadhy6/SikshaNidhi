import urllib.request, json

BASE = 'http://localhost:5000'

def post(path, payload, hdrs={}):
    data = json.dumps(payload).encode()
    h = {'Content-Type': 'application/json'}
    h.update(hdrs)
    req = urllib.request.Request(BASE + path, data=data, headers=h)
    r = urllib.request.urlopen(req, timeout=5)
    return json.loads(r.read().decode())

def get(path, hdrs={}):
    req = urllib.request.Request(BASE + path, headers=hdrs)
    r = urllib.request.urlopen(req, timeout=5)
    return json.loads(r.read().decode())

tests = []

# 1. Health check
d = get('/health')
tests.append(('health', d.get('status') == 'ok', d.get('status')))

# 2. Live scholarships (dashboard page)
d = get('/api/live_scholarships')
count = len(d.get('data', []))
tests.append(('live_scholarships', d.get('status') == 'success' and count > 0, f"{d.get('status')} | {count} items"))

# 3. Notifications
d = get('/api/notifications')
tests.append(('notifications', d.get('status') == 'success', f"{d.get('status')} | {len(d.get('notifications',[]))} alerts"))

# 4. Scholarship search - male (index1.html)
d = post('/api/search', {'age': 20, 'gender': 'Male', 'caste': 'All', 'marks': 70, 'income': 500000})
count = len(d.get('data', []))
tests.append(('search_male_age20', d.get('status') == 'success' and count > 0, f"{d.get('status')} | {count} matches"))

# 5. Scholarship search - female
d = post('/api/search', {'age': 20, 'gender': 'Female', 'caste': 'All', 'marks': 80, 'income': 500000})
count = len(d.get('data', []))
tests.append(('search_female_age20', d.get('status') == 'success' and count > 0, f"{d.get('status')} | {count} matches"))

# 6. SC category search
d = post('/api/search', {'age': 22, 'gender': 'Male', 'caste': 'SC', 'marks': 60, 'income': 200000})
count = len(d.get('data', []))
tests.append(('search_SC_student', d.get('status') == 'success', f"{d.get('status')} | {count} matches"))

# 7. Find opportunities (index2.html)
d = post('/api/find-opportunities', {
    'age': 22, 'state': 'Odisha', 'maritalStatus': 'Single',
    'category': 'General', 'disability': 'No',
    'education': 'Graduate', 'employment': 'Student'
})
tests.append(('find_opportunities', d.get('success') == True and d.get('count', 0) > 0, f"success={d.get('success')} | {d.get('count')} schemes"))

# 8. Feedback submit
d = post('/api/feedback/submit', {
    'user_name': 'FrontendConnectTest', 'rating': 5,
    'message': 'Frontend-backend connectivity verified!',
    'category': 'General', 'page': 'dashboard'
})
tests.append(('feedback_submit', d.get('status') == 'success', d.get('status')))

# 9. Admin verify
d = post('/api/feedback/verify', {'key': 'siksha-admin-2026'})
tests.append(('admin_verify', d.get('status') == 'success', d.get('status')))

# 10. Feedback stats (admin panel)
d = get('/api/feedback/stats', {'X-Admin-Key': 'siksha-admin-2026'})
tests.append(('feedback_stats', d.get('status') == 'success', f"total={d.get('total')} avg_rating={d.get('avg_rating')}"))

# 11. Get all feedback (admin panel)
d = get('/api/feedback/all', {'X-Admin-Key': 'siksha-admin-2026'})
tests.append(('feedback_all', d.get('status') == 'success', f"{d.get('status')} | {len(d.get('data',[]))} records"))

print()
print('=' * 55)
print('   FRONTEND <-> BACKEND CONNECTIVITY REPORT')
print('=' * 55)
passed = 0
for name, ok, detail in tests:
    icon = 'PASS' if ok else 'FAIL'
    print(f'  [{icon}]  {name:28s} {detail}')
    if ok:
        passed += 1

print('=' * 55)
print(f'  Result: {passed}/{len(tests)} tests passed')
print()
print('  Backend :  http://localhost:5000')
print('  Frontend:  http://localhost:5000  (via config.js)')
print('  Database:  SQLite (local, no DATABASE_URL set)')
print('=' * 55)
