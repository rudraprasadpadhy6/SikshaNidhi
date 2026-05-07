import sqlite3
import os
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'data', 'scholarships.db')

def seed_test_data():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check if a test scholarship already exists
    c.execute("SELECT id FROM scholarships WHERE name = 'TEST: Scholarship Ending Soon'")
    if c.fetchone():
        print("Test scholarship already exists. Updating end date...")
        end_date = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
        c.execute("UPDATE scholarships SET close_date = ? WHERE name = 'TEST: Scholarship Ending Soon'", (end_date,))
    else:
        print("Adding test scholarship...")
        end_date = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
        c.execute('''
            INSERT INTO scholarships 
            (name, scholarship_type, amount, description, start_date, close_date, url, min_age, max_age, gender, caste, pwd_only, min_marks, max_income)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('TEST: Scholarship Ending Soon', 'Government', 5000, 'Test description', '2024-01-01', end_date, 'https://example.com', 10, 50, 'All', 'All', False, 0, 1000000))
    
    conn.commit()
    conn.close()
    print(f"Database updated. Test scholarship set to end on {end_date}")

if __name__ == '__main__':
    seed_test_data()
