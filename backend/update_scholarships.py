import sqlite3
import random
import time
from datetime import datetime, timedelta

def get_random_scholarship():
    types = ['Government', 'Private']
    s_type = random.choice(types)
    
    # Generate mock names
    prefixes = ['National', 'State', 'Global', 'Merit', 'Foundation', 'Tech', 'Women in STEM']
    suffixes = ['Grant', 'Fellowship', 'Scholarship', 'Aid Program', 'Endowment']
    name = f"Auto {random.choice(prefixes)} {random.choice(suffixes)} {random.randint(2026, 2030)}"
    
    # Generate dates
    start_dt = datetime.now()
    end_dt = start_dt + timedelta(days=random.randint(30, 365))
    
    amount = random.choice([10000, 25000, 50000, 75000, 100000, 200000])
    
    desc = f"Automatically fetched new {s_type.lower()} scholarship for eligible students. Apply before it closes!"
    url = "https://example-scholarships.org/apply"
    
    # Random criteria
    min_age = random.choice([10, 15, 18])
    max_age = random.choice([25, 30, 35])
    gender = random.choice(['All', 'All', 'Female', 'All'])
    caste = random.choice(['All', 'All', 'SC', 'ST', 'OBC', 'Minority'])
    pwd = random.choice([False, False, True])
    min_marks = random.choice([50, 60, 75, 80])
    max_inc = random.choice([200000, 500000, 800000, 1500000])
    
    return (name, s_type, amount, desc, start_dt.strftime('%Y-%m-%d'), end_dt.strftime('%Y-%m-%d'), 
            url, min_age, max_age, gender, caste, pwd, min_marks, max_inc)

def update_db():
    print("Connecting to database...")
    while True:
        try:
            conn = sqlite3.connect('data/scholarships.db')
            c = conn.cursor()
            
            new_s = get_random_scholarship()
            
            c.execute('''
                INSERT INTO scholarships 
                (name, scholarship_type, amount, description, start_date, close_date, url, min_age, max_age, gender, caste, pwd_only, min_marks, max_income)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', new_s)
            
            conn.commit()
            conn.close()
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] NEW SCHOLARSHIP ADDED: {new_s[0]} ({new_s[1]}) - ₹{new_s[2]}")
            
            # Sleep for 60 seconds before adding another one
            # (In a real scenario, this might run once a day fetching from an API)
            time.sleep(60)
            
        except Exception as e:
            print(f"Error updating database: {e}")
            time.sleep(10)

if __name__ == '__main__':
    print("Starting Automatic Scholarship Updater...")
    update_db()
