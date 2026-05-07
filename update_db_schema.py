import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'data', 'scholarships.db')

def update_schema():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check if documents_required column exists
    c.execute("PRAGMA table_info(scholarships)")
    columns = [row[1] for row in c.fetchall()]
    
    if 'documents_required' not in columns:
        print("Adding 'documents_required' column...")
        c.execute("ALTER TABLE scholarships ADD COLUMN documents_required TEXT DEFAULT 'Aadhar Card, Income Certificate, Last Year Marksheet, Photograph'")
        print("Column added.")
    else:
        print("'documents_required' column already exists.")
    
    # Update some real data for testing
    c.execute('''
        UPDATE scholarships 
        SET documents_required = 'Aadhar Card, 10th/12th Marksheet, Caste Certificate, Income Certificate (if applicable), Bank Passbook'
        WHERE scholarship_type = 'Government'
    ''')
    c.execute('''
        UPDATE scholarships 
        SET documents_required = 'Identity Proof, Admission Letter, Previous Academic Transcripts, Family Income Proof'
        WHERE scholarship_type = 'Private'
    ''')
    
    conn.commit()
    conn.close()
    print("Database schema updated and test data seeded.")

if __name__ == '__main__':
    update_schema()
