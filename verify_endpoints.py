import urllib.request, json

BASE = 'http://localhost:5000'

def post(path, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(BASE + path, data=data, headers={'Content-Type': 'application/json'})
    r = urllib.request.urlopen(req, timeout=5)
    return json.loads(r.read().decode())

def get(path):
    r = urllib.request.urlopen(BASE + path, timeout=5)
    return json.loads(r.read().decode())

print('=== HEALTH ===')
d = get('/health')
print(' ', d)

print()
print('=== LIVE SCHOLARSHIPS ===')
d = get('/api/live_scholarships')
print(f'  Status: {d.get("status")} | Count: {len(d.get("data", []))}')
for s in d.get('data', [])[:5]:
    print(f'  - {s["name"]} | Close: {s["close_date"]}')

print()
print('=== NOTIFICATIONS (closing in 5 days) ===')
d = get('/api/notifications')
print(f'  Status: {d.get("status")} | Count: {len(d.get("notifications", []))}')

print()
print('=== SCHOLARSHIP SEARCH (General Male, age 20, marks 70, income 5L) ===')
d = post('/api/search', {'age': 20, 'gender': 'Male', 'caste': 'All', 'marks': 70, 'income': 500000})
print(f'  Status: {d.get("status")} | Found: {len(d.get("data", []))}')
for s in d.get('data', [])[:5]:
    print(f'  - {s["name"]}')

print()
print('=== SCHOLARSHIP SEARCH (General Female, age 20, marks 80, income 5L) ===')
d = post('/api/search', {'age': 20, 'gender': 'Female', 'caste': 'All', 'marks': 80, 'income': 500000})
print(f'  Status: {d.get("status")} | Found: {len(d.get("data", []))}')
for s in d.get('data', [])[:5]:
    print(f'  - {s["name"]}')

print()
print('=== FIND OPPORTUNITIES (Student, Graduate, age 22) ===')
d = post('/api/find-opportunities', {
    'age': 22, 'state': 'Odisha', 'maritalStatus': 'Single',
    'category': 'General', 'disability': 'No',
    'education': 'Graduate', 'employment': 'Student'
})
print(f'  Success: {d.get("success")} | Count: {d.get("count")}')
for s in d.get('opportunities', [])[:5]:
    desc = s['description'][:60] if isinstance(s['description'], str) else '(html)'
    print(f'  - {desc}...')

print()
print('=== FIND OPPORTUNITIES (Self-Employed, age 28) ===')
d = post('/api/find-opportunities', {
    'age': 28, 'state': 'Odisha', 'maritalStatus': 'Single',
    'category': 'General', 'disability': 'No',
    'education': '12th Pass', 'employment': 'Self-Employed'
})
print(f'  Success: {d.get("success")} | Count: {d.get("count")}')
for s in d.get('opportunities', [])[:5]:
    desc = s['description'][:60] if isinstance(s['description'], str) else '(html)'
    print(f'  - {desc}...')
