import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'schemes.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS financial_schemes')

    cursor.execute('''
    CREATE TABLE financial_schemes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        long_description TEXT,
        why_chosen TEXT,
        official_website TEXT,
        target_states TEXT,
        min_age INTEGER,
        max_age INTEGER,
        marital_status TEXT,
        categories TEXT,
        disability_required BOOLEAN,
        education_levels TEXT,
        employment_statuses TEXT,
        priority INTEGER,
        documents_required TEXT
    )
    ''')
    
    schemes = [
        (
            "Post Matric Scholarship for Minorities",
            "Scholarship for students belonging to minority communities to pursue higher education.",
            "A flagship program providing regular financial assistance to students from minority communities across the nation to support their higher education goals.",
            "Based on your 'Minority' category and 'Student' status, this scheme ensures monetary support for your studies.",
            "https://scholarships.gov.in/",
            json.dumps(["ALL"]), 15, 35, json.dumps([]), json.dumps(["Minority"]), False,
            json.dumps(["10th Pass", "12th Pass", "Graduate", "Postgraduate"]), json.dumps(["Student"]), 10,
            "1. Aadhar Card\n2. Income Certificate\n3. Caste/Minority Certificate\n4. Previous Year Marksheet\n5. Bank Passbook"
        ),
        (
            "Indira Gandhi National Widow Pension Scheme",
            "Provides monthly pension to widows living below poverty line.",
            "A flagship program under the National Social Assistance Programme (NSAP) providing regular, fixed-amount non-contributory pensions to eligible widowed women across the nation.",
            "Based on your 'Widowed' marital status, this scheme ensures a steady flow of foundational monetary support guaranteed by the central government.",
            "https://nsap.nic.in/",
            json.dumps(["ALL"]), 40, 100, json.dumps(["Widow"]), json.dumps([]), False,
            json.dumps([]), json.dumps([]), 8,
            "1. Aadhar Card\n2. Death Certificate of Husband\n3. BPL Card\n4. Age Proof\n5. Bank Passbook"
        ),
        (
            "Deendayal Disabled Rehabilitation Scheme",
            "Financial assistance to provide equal opportunities, equity, and social justice to persons with disabilities.",
            "A comprehensive scheme providing grant-in-aid to NGOs for various projects for rehabilitation of persons with disabilities, ensuring their equal participation.",
            "Based on your 'Disability' status, this program guarantees specialized support and rehabilitation services.",
            "https://disabilityaffairs.gov.in/",
            json.dumps(["ALL"]), 0, 100, json.dumps([]), json.dumps([]), True,
            json.dumps([]), json.dumps([]), 9,
            "1. Disability Certificate (UDID)\n2. Aadhar Card\n3. Income Certificate\n4. Passport Size Photo"
        ),
        (
            "Stand Up India Scheme",
            "Facilitates bank loans between ₹10 lakh and ₹1 crore to SC, ST, and women borrowers.",
            "A government initiative specifically targeting grassroots entrepreneurship to facilitate bank loans for setting up a greenfield enterprise in manufacturing, services or trading sectors.",
            "Based on your background and employment status, this initiative can fund your entrepreneurial goals.",
            "https://www.standupmitra.in/",
            json.dumps(["ALL"]), 18, 100, json.dumps([]), json.dumps(["SC", "ST"]), False,
            json.dumps([]), json.dumps(["Self-Employed", "Working", "Unemployed"]), 7,
            "1. Identity Proof (Aadhar/PAN)\n2. Caste Certificate (if SC/ST)\n3. Project Report\n4. Bank Statements"
        ),
        (
            "PM-SVANidhi",
            "Special Micro-Credit Facility for Street Vendors to resume their livelihoods.",
            "A central sector scheme to facilitate working capital loans up to ₹10,000 for street vendors, completely backed by the government.",
            "Given your Self-Employed status, this provides immediate micro-credit access to support your livelihood.",
            "https://pmsvanidhi.mohua.gov.in/",
            json.dumps(["ALL"]), 18, 100, json.dumps([]), json.dumps([]), False,
            json.dumps([]), json.dumps(["Self-Employed"]), 6,
            "1. Vending Certificate / ID Card issued by ULB\n2. Aadhar Card linked to Mobile\n3. Bank Account details"
        ),
        (
            "National Fellowship for OBC Students",
            "Financial assistance to OBC students for pursuing M.Phil and Ph.D.",
            "A fellowship scheme designed to increase opportunities for higher education (M.Phil/Ph.D) among the OBC community with monthly stipends.",
            "Based on your 'OBC' category and 'Postgraduate' level, this fellowship offers guaranteed stipends for research.",
            "https://socialjustice.gov.in/",
            json.dumps(["ALL"]), 20, 40, json.dumps([]), json.dumps(["OBC"]), False,
            json.dumps(["Postgraduate"]), json.dumps(["Student"]), 9,
            "1. Caste Certificate (OBC Non-Creamy Layer)\n2. Post-Graduation Marksheet\n3. Admission Proof for M.Phil/Ph.D\n4. Aadhar Card"
        ),
        (
            "Pradhan Mantri Kaushal Vikas Yojana (PMKVY)",
            "Skill development initiative scheme to encourage youth for skill training.",
            "The flagship scheme of the Ministry of Skill Development & Entrepreneurship implemented by NSDC to enable youths to take up industry-relevant skill training.",
            "This program directly matches your need for training and certification to boost employment prospects.",
            "https://www.pmkvyofficial.org/",
            json.dumps(["ALL"]), 15, 45, json.dumps([]), json.dumps([]), False,
            json.dumps(["No Schooling", "10th Pass", "12th Pass"]), json.dumps(["Unemployed", "Student"]), 8,
            "1. Aadhar Card\n2. Passport Size Color Photograph\n3. Educational certificates (if any)"
        )
    ]
    
    cursor.executemany('''
        INSERT INTO financial_schemes (
            name, description, long_description, why_chosen, official_website, target_states, min_age, max_age, 
            marital_status, categories, disability_required, education_levels, employment_statuses, priority, documents_required
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', schemes)
    
    conn.commit()
    print("Database re-seeded with extended scheme details.")

    conn.close()

if __name__ == '__main__':
    init_db()
