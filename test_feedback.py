import urllib.request, json

BASE = 'http://localhost:5000'

def post(path, payload, extra_headers={}):
    data = json.dumps(payload).encode()
    h = {'Content-Type': 'application/json'}
    h.update(extra_headers)
    req = urllib.request.Request(BASE + path, data=data, headers=h)
    r = urllib.request.urlopen(req, timeout=5)
    return json.loads(r.read().decode())

def get(path, extra_headers={}):
    req = urllib.request.Request(BASE + path, headers=extra_headers)
    r = urllib.request.urlopen(req, timeout=5)
    return json.loads(r.read().decode())

print('=== FEEDBACK SUBMIT ===')
d = post('/api/feedback/submit', {
    'user_name': 'TestUser', 'rating': 5,
    'message': 'Excellent platform!', 'category': 'General', 'page': 'Home'
})
print(' ', d)

print()
print('=== ADMIN VERIFY ===')
d = post('/api/feedback/verify', {'key': 'siksha-admin-2026'})
print(' ', d)

print()
print('=== FEEDBACK STATS ===')
d = get('/api/feedback/stats', {'X-Admin-Key': 'siksha-admin-2026'})
print(' ', d)

print()
print('=== ALL FEEDBACK ===')
d = get('/api/feedback/all', {'X-Admin-Key': 'siksha-admin-2026'})
status = d.get('status')
count = len(d.get('data', []))
print(f'  Status: {status} | Count: {count}')

print()
print('=== ALL TESTS PASSED ===')
