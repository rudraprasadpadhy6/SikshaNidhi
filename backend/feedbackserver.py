from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import csv
import io
from datetime import datetime
from feedbackdatabase import init_feedback_db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'feedback.db')
FRONTEND_PATH = os.path.join(BASE_DIR, '..', 'frontend')

# Load admin key from .env
from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, '.env'))
ADMIN_KEY = os.getenv('ADMIN_FEEDBACK_KEY', 'siksha-admin-2026')

app = Flask(__name__)
CORS(app)

# Initialize DB on startup
init_feedback_db()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ─────────────────────────────────────────
# USER ROUTE: Submit Feedback
# ─────────────────────────────────────────
@app.route('/api/feedback/submit', methods=['POST'])
def submit_feedback():
    try:
        data = request.json
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400

        rating = int(data.get('rating', 0))
        message = (data.get('message') or '').strip()
        user_name = (data.get('user_name') or 'Anonymous').strip()
        category = data.get('category', 'General')
        page = data.get('page', 'Unknown')

        if not (1 <= rating <= 5):
            return jsonify({'status': 'error', 'message': 'Rating must be between 1 and 5'}), 400
        if not message:
            return jsonify({'status': 'error', 'message': 'Message cannot be empty'}), 400

        conn = get_db()
        c = conn.cursor()
        c.execute(
            'INSERT INTO feedback (user_name, rating, category, message, page) VALUES (?, ?, ?, ?, ?)',
            (user_name, rating, category, message, page)
        )
        conn.commit()
        conn.close()

        return jsonify({'status': 'success', 'message': 'Feedback submitted successfully!'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ─────────────────────────────────────────
# ADMIN ROUTE: Verify Key
# ─────────────────────────────────────────
@app.route('/api/feedback/verify', methods=['POST'])
def verify_admin():
    data = request.json or {}
    key = data.get('key', '')
    if key == ADMIN_KEY:
        return jsonify({'status': 'success', 'message': 'Access granted'})
    return jsonify({'status': 'error', 'message': 'Invalid admin key'}), 403

# ─────────────────────────────────────────
# ADMIN ROUTE: Get All Feedback
# ─────────────────────────────────────────
@app.route('/api/feedback/all', methods=['GET'])
def get_all_feedback():
    key = request.headers.get('X-Admin-Key', '')
    if key != ADMIN_KEY:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM feedback ORDER BY submitted_at DESC')
        rows = c.fetchall()
        conn.close()
        feedback_list = [dict(r) for r in rows]
        return jsonify({'status': 'success', 'data': feedback_list})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ─────────────────────────────────────────
# ADMIN ROUTE: Stats
# ─────────────────────────────────────────
@app.route('/api/feedback/stats', methods=['GET'])
def get_stats():
    key = request.headers.get('X-Admin-Key', '')
    if key != ADMIN_KEY:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT COUNT(*) as total, AVG(rating) as avg_rating FROM feedback')
        row = c.fetchone()
        c.execute('SELECT COUNT(*) as unread FROM feedback WHERE is_read = 0')
        unread = c.fetchone()
        conn.close()
        return jsonify({
            'status': 'success',
            'total': row['total'],
            'avg_rating': round(row['avg_rating'] or 0, 1),
            'unread': unread['unread']
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ─────────────────────────────────────────
# ADMIN ROUTE: Mark as Read
# ─────────────────────────────────────────
@app.route('/api/feedback/mark-read/<int:feedback_id>', methods=['PATCH'])
def mark_read(feedback_id):
    key = request.headers.get('X-Admin-Key', '')
    if key != ADMIN_KEY:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    try:
        conn = get_db()
        conn.execute('UPDATE feedback SET is_read = 1 WHERE id = ?', (feedback_id,))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ─────────────────────────────────────────
# ADMIN ROUTE: Delete Feedback
# ─────────────────────────────────────────
@app.route('/api/feedback/delete/<int:feedback_id>', methods=['DELETE'])
def delete_feedback(feedback_id):
    key = request.headers.get('X-Admin-Key', '')
    if key != ADMIN_KEY:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    try:
        conn = get_db()
        conn.execute('DELETE FROM feedback WHERE id = ?', (feedback_id,))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ─────────────────────────────────────────
# ADMIN ROUTE: Export CSV
# ─────────────────────────────────────────
@app.route('/api/feedback/export', methods=['GET'])
def export_csv():
    key = request.headers.get('X-Admin-Key', '')
    if key != ADMIN_KEY:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT id, user_name, rating, category, message, page, submitted_at, is_read FROM feedback ORDER BY submitted_at DESC')
        rows = c.fetchall()
        conn.close()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'User', 'Rating', 'Category', 'Message', 'Page', 'Submitted At', 'Is Read'])
        for r in rows:
            writer.writerow([r['id'], r['user_name'], r['rating'], r['category'], r['message'], r['page'], r['submitted_at'], 'Yes' if r['is_read'] else 'No'])

        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=SikshaNidhi_Feedback.csv'}
        )
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ─────────────────────────────────────────
# SERVE ADMIN PAGE
# ─────────────────────────────────────────
@app.route('/admin')
def serve_admin():
    return send_from_directory(FRONTEND_PATH, 'feedback_admin.html')

if __name__ == '__main__':
    print("Starting Feedback Server on port 8002...")
    print(f"Admin panel: http://localhost:8002/admin")
    app.run(debug=True, port=8002)
