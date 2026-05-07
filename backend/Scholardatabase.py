import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'scholarships.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create scholarships table
    c.execute('''
        CREATE TABLE IF NOT EXISTS scholarships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            scholarship_type TEXT, 
            amount INTEGER,
            description TEXT,
            start_date TEXT,
            close_date TEXT,
            url TEXT,
            min_age INTEGER,
            max_age INTEGER,
            gender TEXT,
            caste TEXT,
            pwd_only BOOLEAN,
            min_marks INTEGER,
            max_income INTEGER
        )
    ''')
    
    # Clear existing data for a fresh start
    c.execute('DELETE FROM scholarships')
    
    # Insert exhaustive dummy data representing Government and Private scholarships
    # Types: 'Government' and 'Private'
    scholarships = [
        # --- Government Scholarships ---
        ('Post Matric Scholarship for SC', 'Government', 25000, 'Financial assistance to SC students for post-matriculation studies.', '2024-01-01', '2026-12-31', 'https://scholarships.gov.in', 10, 35, 'All', 'SC', False, 50, 250000),
        ('Pragati Scholarship for Girls', 'Government', 50000, 'AICTE scheme to provide encouragement and support to girl children.', '2024-05-01', '2026-12-31', 'https://aicte-india.org', 17, 25, 'Female', 'All', False, 60, 800000),
        ('National Merit-cum-Means Scholarship', 'Government', 12000, 'For meritorious students of economically weaker sections.', '2025-01-01', '2027-01-31', 'https://scholarships.gov.in', 10, 18, 'All', 'All', False, 55, 350000),
        ('KVPY Fellowship', 'Government', 84000, 'Scholarship program to encourage students to take up research careers in Basic Sciences.', '2024-06-01', '2025-12-31', 'http://kvpy.iisc.ac.in', 15, 20, 'All', 'All', False, 75, 1000000),
        ('Pre-Matric Minority Scholarship', 'Government', 10000, 'Financial assistance for minority community students.', '2023-01-01', '2023-12-31', 'https://scholarships.gov.in', 10, 16, 'All', 'Minority', False, 50, 200000), # Expired

        # --- Private Scholarships ---
        ('Tata Trust Medical/Engineering', 'Private', 60000, 'Merit-based scholarship for undergrad students in top institutions.', '2024-07-01', '2026-08-31', 'https://www.tatatrusts.org', 17, 25, 'All', 'All', False, 85, 1200000),
        ('Reliance Foundation Scholarship', 'Private', 200000, 'Supporting India’s brightest youth to fulfill their potential.', '2025-02-01', '2027-01-31', 'https://www.reliancefoundation.org', 18, 30, 'All', 'All', False, 80, 1500000),
        ('Loreal Paris Women in Science', 'Private', 250000, 'Empowering young women pursuing careers in science and STEM fields.', '2024-02-15', '2026-11-30', 'https://www.loreal.com', 17, 25, 'Female', 'All', False, 85, 600000),
        ('Special Ability Tech Grant', 'Private', 75000, 'Grant for students with benchmark disabilities pursuing technology.', '2025-01-01', '2026-12-31', 'https://pwd-grants.org', 15, 35, 'All', 'All', True, 50, 1500000),
        ('HDFC Badhte Kadam Scholarship', 'Private', 100000, 'Supports students who have faced hard times to continue education.', '2023-05-01', '2024-03-31', 'https://hdfcbank.com', 18, 28, 'All', 'All', False, 60, 600000) # Expired
    ]
    
    c.executemany('''
        INSERT INTO scholarships 
        (name, scholarship_type, amount, description, start_date, close_date, url, min_age, max_age, gender, caste, pwd_only, min_marks, max_income)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', scholarships)
    
    conn.commit()
    conn.close()
    print(f"Database created at {DB_PATH} with fresh active and expired data.")

if __name__ == '__main__':
    init_db()
