import os
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# In-Memory Datasets for Vercel Serverless API
SCHOLARSHIPS_DATA = [
    {
        "name": "Post Matric Scholarship for SC",
        "type": "Government",
        "close_date": "2026-12-31",
        "amt": 25000,
        "url": "https://scholarships.gov.in",
        "docs": "1. Aadhar Card\n2. Income Certificate\n3. Caste Certificate\n4. Marksheet\n5. Bank Passbook",
        "status": "Ongoing"
    },
    {
        "name": "Pragati Scholarship for Girls",
        "type": "Government",
        "close_date": "2026-12-31",
        "amt": 50000,
        "url": "https://aicte-india.org",
        "docs": "1. Aadhar Card\n2. Income Certificate\n3. Marksheet\n4. Admission Letter",
        "status": "Ongoing"
    },
    {
        "name": "National Merit-cum-Means Scholarship",
        "type": "Government",
        "close_date": "2027-01-31",
        "amt": 12000,
        "url": "https://scholarships.gov.in",
        "docs": "1. Aadhar Card\n2. Income Certificate\n3. Marksheet",
        "status": "Ongoing"
    },
    {
        "name": "Tata Trust Medical/Engineering",
        "type": "Private",
        "close_date": "2026-08-31",
        "amt": 60000,
        "url": "https://www.tatatrusts.org",
        "docs": "1. Aadhar Card\n2. College ID\n3. Marksheet\n4. Fee Receipt",
        "status": "Ongoing"
    },
    {
        "name": "Reliance Foundation Scholarship",
        "type": "Private",
        "close_date": "2027-01-31",
        "amt": 200000,
        "url": "https://www.reliancefoundation.org",
        "docs": "1. Aadhar Card\n2. Income Proof\n3. Academic Records",
        "status": "Ongoing"
    }
]

FINANCIAL_SCHEMES_DATA = [
    {
        "name": "Post Matric Scholarship for Minorities",
        "description": "Scholarship for students belonging to minority communities to pursue higher education.",
        "url": "https://scholarships.gov.in/",
        "priority_score": 10
    },
    {
        "name": "Deendayal Disabled Rehabilitation Scheme",
        "description": "Financial assistance to provide equal opportunities, equity, and social justice to persons with disabilities.",
        "url": "https://disabilityaffairs.gov.in/",
        "priority_score": 9
    },
    {
        "name": "Indira Gandhi National Widow Pension Scheme",
        "description": "Provides monthly pension to widows living below poverty line.",
        "url": "https://nsap.nic.in/",
        "priority_score": 8
    },
    {
        "name": "Stand Up India Scheme",
        "description": "Facilitates bank loans between ₹10 lakh and ₹1 crore to SC, ST, and women borrowers.",
        "url": "https://www.standupmitra.in/",
        "priority_score": 7
    }
]

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "message": "SikshaNidhi Engine Live",
        "environment": "In-Memory Engine (Database-Free)"
    })

@app.route('/api/live_scholarships', methods=['GET'])
def live_scholarships():
    return jsonify({"data": SCHOLARSHIPS_DATA, "status": "success"}), 200

@app.route('/api/live_schemes', methods=['GET'])
def live_schemes():
    return jsonify({"data": FINANCIAL_SCHEMES_DATA, "status": "success"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)