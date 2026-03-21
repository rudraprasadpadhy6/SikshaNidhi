import http.server
import socketserver
import json
import sqlite3
import os

PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', '..', 'data', 'schemes.db')
DIRECTORY = os.path.join(BASE_DIR, '..', '..')

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_POST(self):
        if self.path == '/api/find-opportunities':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                age = int(data.get('age', 0))
                state = data.get('state', '')
                marital_status = data.get('maritalStatus', '')
                category = data.get('category', '')
                disability = data.get('disability', 'No') == 'Yes'
                education = data.get('education', '')
                employment = data.get('employment', '')
                
                # Query DB
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM financial_schemes')
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()
                conn.close()
                
                eligible_schemes = []
                for row in rows:
                    scheme = dict(zip(columns, row))
                    
                    # Age check
                    if scheme['min_age'] is not None and age < scheme['min_age']: continue
                    if scheme['max_age'] is not None and age > scheme['max_age']: continue
                    
                    # Target States check
                    target_states = json.loads(scheme['target_states'] or '["ALL"]')
                    if "ALL" not in target_states and state not in target_states: continue
                    
                    # Marital Status check
                    valid_ms = json.loads(scheme['marital_status'] or '[]')
                    if valid_ms and marital_status not in valid_ms: continue
                    
                    # Category check
                    valid_categories = json.loads(scheme['categories'] or '[]')
                    if valid_categories and category not in valid_categories: continue
                    
                    # Disability check
                    if scheme['disability_required'] and not disability: continue
                    
                    # Education check
                    valid_edu = json.loads(scheme['education_levels'] or '[]')
                    if valid_edu and education not in valid_edu: continue
                    
                    # Employment check
                    valid_emp = json.loads(scheme['employment_statuses'] or '[]')
                    if valid_emp and employment not in valid_emp: continue
                    
                    html_payload = f'''
                    <span style="cursor:pointer; color:#054c5a; text-decoration:underline; display:block; padding:5px 0;" onclick="
                        if(window.event) window.event.preventDefault();
                        const template = document.getElementById('details-{scheme["id"]}').innerHTML;
                        const container = document.getElementById('success-screen');
                        if(!window.originalListCache) window.originalListCache = container.innerHTML;
                        container.innerHTML = template;
                        ">
                        {scheme['name']} <small style="color:#4dcbc6; font-size:14px; margin-left:10px; font-weight:normal;">(Click for details)</small>
                    </span>
                    <template id="details-{scheme['id']}">
                        <div style="text-align: left; padding: 10px; font-family: 'Segoe UI', sans-serif;">
                            <h2 style="color: #0b5b6a; margin-bottom: 15px; font-size: 34px; line-height: 1.2;">{scheme['name']}</h2>
                            <p style="color: #666; font-size: 20px; margin-bottom: 35px;">{scheme['description']}</p>
                            
                            <div style="background-color: #e8f8f9; padding: 25px; border-radius: 12px; margin-bottom: 25px;">
                                <h3 style="color: #0b5b6a; margin-top: 0; font-size: 22px; font-weight: 600;">About This Opportunity</h3>
                                <p style="color: #444; margin-bottom: 0; font-size: 18px; line-height: 1.6;">{scheme['long_description']}</p>
                            </div>
                            
                            <div style="background-color: #e8f8f9; padding: 25px; border-radius: 12px; margin-bottom: 40px;">
                                <h3 style="color: #0b5b6a; margin-top: 0; font-size: 22px; font-weight: 600;">Why We Chose This For You</h3>
                                <p style="color: #444; margin-bottom: 0; font-size: 18px; line-height: 1.6;">{scheme['why_chosen']}</p>
                            </div>
                            
                            <div style="display: flex; gap: 20px;">
                                <button onclick="document.getElementById('success-screen').innerHTML = window.originalListCache; window.originalListCache = null;" style="background-color: #e8f8f9; color: #4dcbc6; padding: 20px 30px; font-size: 22px; font-weight: 600; border: none; border-radius: 12px; cursor: pointer; flex: 1; transition: 0.2s;">Back to List</button>
                                <a href="{scheme['official_website']}" target="_blank" style="background-color: #4dcbc6; color: white; padding: 20px 30px; font-size: 22px; font-weight: 600; border: none; border-radius: 12px; cursor: pointer; text-decoration: none; text-align: center; flex: 1; display: inline-block; transition: 0.2s;">Official Website</a>
                            </div>
                        </div>
                    </template>
                    '''
                    
                    eligible_schemes.append({
                        'name': html_payload,
                        'description': scheme['description'],
                        'official_website': scheme['official_website'],
                        'priority': scheme['priority']
                    })
                
                # Sort by priority descending
                eligible_schemes.sort(key=lambda x: x['priority'], reverse=True)
                
                response = {
                    'success': True,
                    'count': len(eligible_schemes),
                    'opportunities': eligible_schemes
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*') # Enable CORS
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
                
        elif self.path == '/api/add-opportunity':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                
                name = data.get('name', 'Untitled Scheme')
                description = data.get('description', '')
                long_description = data.get('long_description', '')
                why_chosen = data.get('why_chosen', '')
                official_website = data.get('official_website', '')
                target_states = json.dumps(data.get('target_states', ["ALL"]))
                min_age = data.get('min_age', None)
                max_age = data.get('max_age', None)
                marital_status = json.dumps(data.get('marital_status', []))
                categories = json.dumps(data.get('categories', []))
                disability_required = data.get('disability_required', False)
                education_levels = json.dumps(data.get('education_levels', []))
                employment_statuses = json.dumps(data.get('employment_statuses', []))
                priority = data.get('priority', 5)
                
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO financial_schemes (
                        name, description, long_description, why_chosen, official_website, target_states, min_age, max_age, 
                        marital_status, categories, disability_required, education_levels, employment_statuses, priority
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (name, description, long_description, why_chosen, official_website, target_states, min_age, max_age, 
                      marital_status, categories, disability_required, education_levels, employment_statuses, priority))
                conn.commit()
                new_id = cursor.lastrowid
                conn.close()
                
                response = {'success': True, 'id': new_id, 'message': 'New opportunity added successfully'}
                self.send_response(201)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    # Enable CORS for preflight requests
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == '__main__':
    import database
    database.init_db()
    
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print(f"Server serving at port {PORT}")
        print(f"API Endpoint: http://localhost:{PORT}/api/find-opportunities")
        httpd.serve_forever()
