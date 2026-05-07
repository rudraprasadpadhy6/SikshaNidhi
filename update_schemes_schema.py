import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'data', 'schemes.db')

def update_schemes_schema():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check if documents_required column exists
    c.execute("PRAGMA table_info(financial_schemes)")
    columns = [row[1] for row in c.fetchall()]
    
    if 'documents_required' not in columns:
        print("Adding 'documents_required' column to financial_schemes...")
        c.execute("ALTER TABLE financial_schemes ADD COLUMN documents_required TEXT DEFAULT 'Identity Proof, Residence Proof, Income Certificate, Bank Details'")
        print("Column added.")
    else:
        print("'documents_required' column already exists.")
    
    # Update some real data for testing
    c.execute('''
        UPDATE financial_schemes 
        SET documents_required = 'Aadhar Card, PAN Card, Last 6 Months Bank Statement, Salary Slips'
        WHERE name LIKE '%Loan%' OR name LIKE '%Credit%'
    ''')
    c.execute('''
        UPDATE financial_schemes 
        SET documents_required = 'Caste Certificate, Domicile Certificate, Previous Year Marksheet, Fee Receipt'
        WHERE name LIKE '%Scholarship%' OR name LIKE '%Grant%'
    ''')
    
    conn.commit()
    conn.close()
    print("Schemes database schema updated and test data seeded.")

if __name__ == '__main__':
    update_schemes_schema()
