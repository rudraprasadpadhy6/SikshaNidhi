import os
import sys
import json

# Make db_helper importable from root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'backend'))

from db_helper import get_db_connection, is_postgres

# ─────────────────────────────────────────────────
#  SCHOLARSHIPS
# ─────────────────────────────────────────────────
def seed_scholarships():
    conn = get_db_connection('scholarships')

    if is_postgres():
        conn.execute('''CREATE TABLE IF NOT EXISTS scholarships (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            scholarship_type TEXT NOT NULL,
            amount INTEGER NOT NULL,
            description TEXT,
            start_date TEXT,
            close_date TEXT,
            url TEXT,
            min_age INTEGER DEFAULT 0,
            max_age INTEGER DEFAULT 100,
            gender TEXT DEFAULT 'All',
            caste TEXT DEFAULT 'All',
            pwd_only INTEGER DEFAULT 0,
            min_marks INTEGER DEFAULT 0,
            max_income INTEGER DEFAULT 9999999,
            documents_required TEXT
        )''')
    else:
        conn.execute('''CREATE TABLE IF NOT EXISTS scholarships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            scholarship_type TEXT NOT NULL,
            amount INTEGER NOT NULL,
            description TEXT,
            start_date TEXT,
            close_date TEXT,
            url TEXT,
            min_age INTEGER DEFAULT 0,
            max_age INTEGER DEFAULT 100,
            gender TEXT DEFAULT 'All',
            caste TEXT DEFAULT 'All',
            pwd_only INTEGER DEFAULT 0,
            min_marks INTEGER DEFAULT 0,
            max_income INTEGER DEFAULT 9999999,
            documents_required TEXT
        )''')

    # Wipe existing data
    conn.execute('DELETE FROM scholarships')
    conn.commit()

    scholarships = [
        # GOVERNMENT — General category, open to all
        ('National Merit-cum-Means Scholarship', 'Government', 12000,
         'Awarded by Ministry of Education to meritorious students from economically weaker sections studying in Classes 9-12.',
         '2026-01-01', '2027-01-31', 'https://scholarships.gov.in',
         10, 18, 'All', 'All', 0, 55, 350000,
         '1. Aadhar Card\n2. Income Certificate\n3. Previous Marksheet\n4. Bank Passbook\n5. School Bonafide Certificate'),

        ('Central Sector Scheme of Scholarship', 'Government', 20000,
         'Scholarship for college & university students who are in top 20 percentile in 12th board exams.',
         '2026-01-01', '2027-03-31', 'https://scholarships.gov.in',
         17, 25, 'All', 'All', 0, 80, 800000,
         '1. Aadhar Card\n2. 12th Marksheet\n3. Income Certificate\n4. Bank Passbook\n5. College Admission Proof'),

        ('Prime Minister Scholarship Scheme (PMSS)', 'Government', 36000,
         'For wards of ex-servicemen/ex-coast guard. Covers professional degree programs.',
         '2026-02-01', '2026-11-30', 'https://ksb.gov.in/pm-scholarship.htm',
         17, 30, 'All', 'All', 0, 60, 9999999,
         '1. Aadhar Card\n2. ESM Certificate\n3. Bonafide Certificate\n4. Bank Passbook\n5. Marksheet'),

        ('Pragati Scholarship for Girls (AICTE)', 'Government', 50000,
         'For girl students admitted to AICTE-approved institutions for diploma or degree programs in technical education.',
         '2026-01-01', '2026-12-31', 'https://www.aicte-india.org/bureaus/scholarships',
         17, 30, 'Female', 'All', 0, 60, 800000,
         '1. Aadhar Card\n2. Income Certificate\n3. Admission Letter\n4. Bank Passbook\n5. Passport Photo'),

        ('Saksham Scholarship (AICTE)', 'Government', 50000,
         'For specially-abled students pursuing technical education in AICTE-approved institutions.',
         '2026-01-01', '2026-12-31', 'https://www.aicte-india.org/bureaus/scholarships',
         17, 30, 'All', 'All', 1, 60, 800000,
         '1. Aadhar Card\n2. Disability Certificate\n3. Admission Letter\n4. Bank Passbook'),

        ('Post Matric Scholarship for SC Students', 'Government', 25000,
         'Financial assistance to SC students studying at post-matriculation or post-secondary stage.',
         '2026-01-01', '2026-12-31', 'https://scholarships.gov.in',
         10, 35, 'All', 'SC', 0, 50, 250000,
         '1. Aadhar Card\n2. Caste Certificate\n3. Income Certificate\n4. Previous Marksheet\n5. Bank Passbook'),

        ('Post Matric Scholarship for ST Students', 'Government', 25000,
         'Financial assistance to ST students studying at post-matriculation or post-secondary stage.',
         '2026-01-01', '2026-12-31', 'https://tribal.nic.in',
         10, 35, 'All', 'ST', 0, 50, 250000,
         '1. Aadhar Card\n2. Tribe Certificate\n3. Income Certificate\n4. Previous Marksheet\n5. Bank Passbook'),

        ('Post Matric Scholarship for OBC Students', 'Government', 20000,
         'Scholarship for OBC students to pursue post-matriculation studies.',
         '2026-01-01', '2026-12-31', 'https://scholarships.gov.in',
         10, 35, 'All', 'OBC', 0, 50, 300000,
         '1. Aadhar Card\n2. OBC Certificate\n3. Income Certificate\n4. Marksheet\n5. Bank Passbook'),

        ('Pre-Matric Scholarship for Minorities', 'Government', 10000,
         'For students from minority communities in classes 1-10 to prevent dropout.',
         '2026-01-01', '2026-12-15', 'https://scholarships.gov.in',
         10, 16, 'All', 'Minority', 0, 50, 200000,
         '1. Aadhar Card\n2. Minority Certificate\n3. Income Certificate\n4. School Bonafide\n5. Bank Passbook'),

        ('KVPY Fellowship (Kishore Vaigyanik Protsahan Yojana)', 'Government', 80000,
         'National fellowship program by DST for students interested in basic science courses.',
         '2026-03-01', '2027-01-15', 'https://kvpy.iisc.ac.in',
         15, 20, 'All', 'All', 0, 75, 1000000,
         '1. Aadhar Card\n2. Class 10 / 12 Marksheet\n3. Income Certificate\n4. Bank Passbook'),

        ('Odisha State Merit Scholarship', 'Government', 15000,
         'State government scholarship for meritorious students from Odisha passing 10th standard.',
         '2026-04-01', '2026-11-30', 'https://scholarships.odisha.gov.in',
         14, 22, 'All', 'All', 0, 60, 600000,
         '1. Aadhar Card\n2. Income Certificate\n3. 10th Marksheet\n4. Residential Certificate\n5. Bank Passbook'),

        # PRIVATE
        ('Tata Trust Scholarship (Tech & Medical)', 'Private', 120000,
         'Tata Trusts fund meritorious students from low-income families pursuing engineering/medicine.',
         '2026-04-01', '2026-08-31', 'https://www.tatatrusts.org/our-work/education',
         17, 25, 'All', 'All', 0, 85, 1200000,
         '1. Aadhar Card\n2. Income Certificate\n3. Admission Letter\n4. Marksheet\n5. Bank Passbook'),

        ('Reliance Foundation Scholarship', 'Private', 200000,
         'For undergraduate students in engineering, basic sciences, humanities & liberal arts, and business management.',
         '2026-05-01', '2027-01-31', 'https://scholarships.reliancefoundation.org',
         18, 30, 'All', 'All', 0, 80, 1500000,
         '1. Aadhar Card\n2. Income Certificate\n3. Admission Letter\n4. 12th Marksheet\n5. Bank Passbook'),

        ('Loreal Paris For Women in Science', 'Private', 250000,
         'Recognizes exceptional women scientists and supports their scientific research.',
         '2026-06-01', '2026-11-30', 'https://www.loreal.com/en/india/articles/commitments/l-oreal-india-for-women-in-science/',
         17, 25, 'Female', 'All', 0, 85, 600000,
         '1. Aadhar Card\n2. Income Certificate\n3. Research Proposal\n4. Marksheet\n5. College ID'),

        ('HDFC Badhte Kadam Scholarship', 'Private', 75000,
         'HDFC Bank scholarship for students from low-income families enrolled in degree or diploma programs.',
         '2026-05-01', '2026-12-31', 'https://www.hdfcbank.com/personal/resources/learning-centre/borrow/hdfc-bank-scholarship',
         18, 28, 'All', 'All', 0, 60, 600000,
         '1. Aadhar Card\n2. Income Certificate\n3. Admission Proof\n4. Marksheet\n5. Bank Passbook'),

        ('Infosys BPM Scholarship', 'Private', 100000,
         'Merit-based scholarship for engineering students with strong academic record.',
         '2026-05-01', '2026-10-31', 'https://www.infosysbpm.com/corporate-social-responsibility',
         18, 25, 'All', 'All', 0, 75, 900000,
         '1. Aadhar Card\n2. College Bonafide\n3. Income Certificate\n4. Marksheet\n5. Bank Passbook'),

        ('Wipro Cares Scholarship', 'Private', 60000,
         'Wipro Cares supports students from economically disadvantaged backgrounds in their engineering studies.',
         '2026-05-01', '2026-09-30', 'https://www.wipro.com/wipro-cares/',
         18, 25, 'All', 'All', 0, 70, 500000,
         '1. Aadhar Card\n2. Income Certificate\n3. Bonafide Certificate\n4. Marksheet\n5. Bank Passbook'),

        ("Dr. Reddy's Foundation Scholarship", 'Private', 40000,
         'Provides vocational training and livelihood support to underprivileged youth.',
         '2026-04-01', '2026-12-31', 'https://drreddysfoundation.org',
         18, 30, 'All', 'All', 0, 50, 400000,
         '1. Aadhar Card\n2. Income Certificate\n3. Education Proof\n4. Bank Passbook'),

        ('Special Ability Tech Grant', 'Private', 90000,
         'Technology grant for specially-abled students pursuing engineering or IT programs.',
         '2026-03-01', '2026-12-31', 'https://specialabilitytech.org',
         15, 35, 'All', 'All', 1, 50, 1500000,
         '1. Aadhar Card\n2. Disability Certificate\n3. Admission Proof\n4. Marksheet\n5. Bank Passbook'),

        ('Aga Khan Foundation Scholarship', 'Private', 100000,
         'Scholarship for postgraduate study abroad — for students from developing countries with outstanding academic merit and financial need.',
         '2026-04-01', '2026-09-15', 'https://www.akdn.org/our-agencies/aga-khan-foundation/international-scholarship-programme',
         22, 35, 'All', 'All', 0, 70, 500000,
         '1. Aadhar Card\n2. Postgraduate Admission Letter\n3. Income Certificate\n4. Recommendation Letters\n5. Bank Passbook'),
    ]

    c = conn.cursor()
    c.executemany('''INSERT INTO scholarships
        (name, scholarship_type, amount, description, start_date, close_date, url,
         min_age, max_age, gender, caste, pwd_only, min_marks, max_income, documents_required)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', scholarships)

    conn.commit()
    conn.close()
    print(f'Seeded {len(scholarships)} scholarships.')


# ─────────────────────────────────────────────────
#  SCHEMES
# ─────────────────────────────────────────────────
def seed_schemes():
    conn = get_db_connection('schemes')

    if is_postgres():
        conn.execute('''CREATE TABLE IF NOT EXISTS financial_schemes (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            long_description TEXT,
            why_chosen TEXT,
            official_website TEXT,
            target_states TEXT DEFAULT \'["ALL"]\',
            min_age INTEGER DEFAULT 0,
            max_age INTEGER DEFAULT 100,
            marital_status TEXT DEFAULT \'[]\',
            categories TEXT DEFAULT \'[]\',
            disability_required INTEGER DEFAULT 0,
            education_levels TEXT DEFAULT \'[]\',
            employment_statuses TEXT DEFAULT \'[]\',
            priority INTEGER DEFAULT 5,
            documents_required TEXT
        )''')
    else:
        conn.execute('''CREATE TABLE IF NOT EXISTS financial_schemes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            long_description TEXT,
            why_chosen TEXT,
            official_website TEXT,
            target_states TEXT DEFAULT '["ALL"]',
            min_age INTEGER DEFAULT 0,
            max_age INTEGER DEFAULT 100,
            marital_status TEXT DEFAULT '[]',
            categories TEXT DEFAULT '[]',
            disability_required INTEGER DEFAULT 0,
            education_levels TEXT DEFAULT '[]',
            employment_statuses TEXT DEFAULT '[]',
            priority INTEGER DEFAULT 5,
            documents_required TEXT
        )''')

    conn.execute('DELETE FROM financial_schemes')
    conn.commit()

    schemes = [
        # ── GENERAL / OPEN TO ALL ──────────────────────────────────────────
        ('PM Jan Dhan Yojana',
         'Financial inclusion scheme offering zero-balance bank accounts with RuPay debit cards and accident insurance.',
         'Pradhan Mantri Jan Dhan Yojana (PMJDY) is a national mission for financial inclusion. It ensures access to financial services — savings, remittance, credit, insurance, and pension — in an affordable manner. Account holders receive a free RuPay debit card and Rs.2 lakh accidental insurance cover.',
         'This foundational scheme ensures you have a linked bank account for receiving all government benefit transfers (DBT) directly, which is required for most other schemes.',
         'https://pmjdy.gov.in',
         '["ALL"]', 18, 100, '[]', '[]', 0, '[]', '[]', 10,
         '1. Aadhar Card\n2. PAN Card (if available)\n3. Passport Photo\n4. Address Proof'),

        ('Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY)',
         'Government-backed life insurance scheme offering Rs.2 lakh cover at just Rs.436/year premium.',
         "PMJJBY is a one-year life insurance scheme, renewable from year to year, offering coverage for death due to any reason. The premium is Rs.436 per annum and is auto-debited from the subscriber's bank account. Coverage is Rs.2 lakh for a nominee on the death of the insured.",
         'With a minimal premium of just Rs.436/year, this scheme provides strong financial safety for your family, making it ideal for students and working individuals alike.',
         'https://jansuraksha.gov.in',
         '["ALL"]', 18, 50, '[]', '[]', 0, '[]', '[]', 9,
         '1. Aadhar Card\n2. Bank Account (Jan Dhan or regular)\n3. Consent Form'),

        ('Pradhan Mantri Suraksha Bima Yojana (PMSBY)',
         'Accidental insurance scheme offering Rs.2 lakh cover at just Rs.20/year.',
         'PMSBY is an accident insurance scheme that offers coverage for accidental death or disability. The premium is just Rs.20 per annum. In case of accidental death or permanent total disability, Rs.2 lakh is paid; for permanent partial disability, Rs.1 lakh is paid.',
         'For as low as Rs.20 per year, you and your family get financial protection against accidents — making it one of the best and most affordable safety nets available.',
         'https://jansuraksha.gov.in',
         '["ALL"]', 18, 70, '[]', '[]', 0, '[]', '[]', 9,
         '1. Aadhar Card\n2. Bank Account\n3. Consent Form'),

        ('Atal Pension Yojana (APY)',
         'Government pension scheme guaranteeing monthly pension of Rs.1,000–5,000 after age 60.',
         "Atal Pension Yojana is a pension scheme focused on the unorganized sector workers. Under APY, a subscriber will receive a fixed minimum monthly pension of Rs.1,000 to Rs.5,000 per month from age 60, based on contribution. The government co-contributes 50% of the subscriber's contribution or Rs.1,000 per annum, whichever is lower.",
         'Start early, retire comfortably. This scheme is perfect for students and young professionals looking to build a secure retirement corpus with government co-contribution benefits.',
         'https://npscra.nsdl.co.in/scheme-details.php',
         '["ALL"]', 18, 40, '[]', '[]', 0, '[]', '[]', 8,
         '1. Aadhar Card\n2. Bank Account\n3. Mobile Number'),

        ('Pradhan Mantri Mudra Yojana (PMMY)',
         'Loans up to Rs.10 lakh for non-corporate, non-farm small/micro enterprises.',
         'Under PMMY, loans are provided under three categories: Shishu (up to Rs.50,000), Kishor (Rs.50,001–5 lakh), and Tarun (Rs.5–10 lakh). These loans are extended without collateral to help micro-enterprises, startups, and small businesses thrive.',
         'If you want to start or grow a small business, MUDRA provides collateral-free loans to help you get started — ideal for young entrepreneurs and self-employed individuals.',
         'https://www.mudra.org.in',
         '["ALL"]', 18, 65, '[]', '[]', 0, '[]', '["Self-Employed", "Unemployed", "Working"]', 9,
         '1. Aadhar Card\n2. PAN Card\n3. Business Plan\n4. Bank Statement\n5. Address Proof'),

        ('PM Kaushal Vikas Yojana (PMKVY)',
         'Free skill training program for Indian youth to gain industry-relevant skills and certification.',
         'PMKVY is the flagship scheme of the Ministry of Skill Development & Entrepreneurship (MSDE). It enables Indian youth to take up industry-relevant skill training that will help them secure a better livelihood. The scheme provides monetary rewards and recognition certificates to trainees.',
         'If you are looking to gain practical, job-ready skills or switch careers, PMKVY offers free training in over 300 job roles across 38 sectors with placement assistance.',
         'https://www.pmkvyofficial.org',
         '["ALL"]', 15, 45, '[]', '[]', 0,
         '["No Schooling", "10th Pass", "12th Pass", "Graduate"]',
         '["Unemployed", "Student"]', 9,
         '1. Aadhar Card\n2. Educational Certificate\n3. Passport Photo\n4. Bank Passbook'),

        ('Digital India Internship Scheme',
         'Paid internship opportunities in government digital projects for youth and graduates.',
         'The Digital India Internship Scheme provides internship opportunities for students and youth in government projects related to digitization, IT, e-governance, and digital services. Interns get stipends and real project experience.',
         'If you are a graduate or student in IT/CS, this internship gives you a foot in the door for government tech projects while earning a stipend.',
         'https://digitalindia.gov.in',
         '["ALL"]', 18, 35, '[]', '[]', 0,
         '["12th Pass", "Graduate", "Postgraduate"]',
         '["Student", "Unemployed"]', 7,
         '1. Aadhar Card\n2. College/University ID\n3. Resume\n4. Bank Passbook'),

        # ── WOMEN-FOCUSED ─────────────────────────────────────────────────
        ('Mahila Shakti Kendra (MSK)',
         'Empowers rural women through community engagement and training in government schemes.',
         'Mahila Shakti Kendra aims to empower rural women with opportunities for skill development, employment, digital literacy, health awareness, and nutrition. It works through student volunteers and community resource persons.',
         'If you are a rural woman seeking community empowerment, skill training, or access to government welfare, MSK connects you with local resources and government support.',
         'https://wcd.nic.in/schemes-listing/3298',
         '["ALL"]', 18, 60, '[]', '[]', 0, '[]', '[]', 7,
         '1. Aadhar Card\n2. Address Proof\n3. Passport Photo'),

        ('Pradhan Mantri Matru Vandana Yojana (PMMVY)',
         'Maternity benefit of Rs.5,000 for first live birth to support working women.',
         'PMMVY is a maternity benefit program under which pregnant and lactating mothers get cash incentive of Rs.5,000 in three installments for the first living child. The benefit is to compensate for wage loss, improve health and nutrition, and cover part of birth-related expenses.',
         'For expectant mothers, PMMVY provides direct financial support to ensure better nutrition and healthcare during pregnancy and after childbirth.',
         'https://pmmvy.wcd.gov.in',
         '["ALL"]', 19, 50, '["Married"]', '[]', 0, '[]', '[]', 8,
         "1. Aadhar Card\n2. MCP Card\n3. Bank Passbook\n4. Husband's Aadhar"),

        ('Beti Bachao Beti Padhao',
         'Government initiative to prevent gender-biased sex selective elimination and promote girl child education.',
         "This scheme aims to address the declining Child Sex Ratio and issues related to empowerment of women over a life cycle continuum. It promotes welfare of the girl child through various awareness campaigns and direct intervention schemes.",
         "If you are a girl student or parent of a girl child, this scheme provides scholarships, awareness programs, and educational support to promote girls' education.",
         'https://wcd.nic.in/bbbp-schemes',
         '["ALL"]', 0, 21, '[]', '[]', 0, '[]', '[]', 8,
         '1. Aadhar Card\n2. Birth Certificate\n3. School Enrollment Proof'),

        # ── SC/ST/OBC ─────────────────────────────────────────────────────
        ('Post Matric Scholarship for SC Students',
         'Financial assistance to SC students at post-matriculation or post-secondary education stage.',
         'The scheme provides financial assistance to SC students pursuing post-matriculation or post-secondary education. The scholarship covers maintenance allowance, study tour charges, thesis typing/printing charges, and other specific allowances.',
         'If you belong to the SC category, this scholarship ensures you can complete your higher education without financial barriers, covering tuition, living expenses, and study materials.',
         'https://scholarships.gov.in/fresh/newstdRegn',
         '["ALL"]', 14, 35, '[]', '["SC"]', 0,
         '["10th Pass", "12th Pass", "Graduate", "Postgraduate"]',
         '["Student"]', 10,
         '1. Aadhar Card\n2. SC Certificate\n3. Income Certificate\n4. Marksheet\n5. Bank Passbook'),

        ('Post Matric Scholarship for ST Students',
         'Scholarship for ST students to cover education expenses at post-matric level.',
         'This scheme provides financial assistance to students belonging to Scheduled Tribes for pursuing post-matriculation or post-secondary education in recognized institutions. Covers maintenance and other education-related allowances.',
         'If you belong to the ST category, this scheme provides crucial financial support for your post-10th education, removing economic barriers to higher education.',
         'https://tribal.nic.in/index.aspx',
         '["ALL"]', 14, 35, '[]', '["ST"]', 0,
         '["10th Pass", "12th Pass", "Graduate", "Postgraduate"]',
         '["Student"]', 10,
         '1. Aadhar Card\n2. ST Certificate\n3. Income Certificate\n4. Marksheet\n5. Bank Passbook'),

        ('Stand Up India Scheme',
         'Bank loans from Rs.10 lakh to Rs.1 crore for SC/ST and women entrepreneurs.',
         'Stand Up India facilitates bank loans between Rs.10 lakh and Rs.1 crore to at least one SC or ST borrower and at least one woman borrower per bank branch for setting up a greenfield enterprise in manufacturing, services, agri-allied activities, or trading sector.',
         'If you are an SC/ST entrepreneur or a woman wanting to start a business, Stand Up India provides significant loan support with minimal procedural hurdles.',
         'https://www.standupmitra.in',
         '["ALL"]', 18, 65, '[]', '["SC", "ST"]', 0, '[]',
         '["Self-Employed", "Unemployed", "Working"]', 9,
         '1. Aadhar Card\n2. Caste Certificate\n3. Business Plan\n4. Bank Statement\n5. PAN Card'),

        ('National Fellowship for OBC Students',
         'Fellowship for OBC students pursuing M.Phil/PhD at recognized Indian universities.',
         'The National Fellowship for OBC Students provides financial assistance to OBC students to pursue M.Phil/PhD at university/institutions recognized by UGC. Fellows receive JRF stipend and HRA as applicable under UGC norms.',
         'If you are an OBC student aspiring to pursue research (M.Phil/PhD), this fellowship offers a competitive stipend to support your academic ambitions.',
         'https://scholarships.gov.in',
         '["ALL"]', 20, 40, '[]', '["OBC"]', 0,
         '["Graduate", "Postgraduate"]',
         '["Student"]', 9,
         '1. Aadhar Card\n2. OBC Certificate\n3. Graduation Certificate\n4. University Admission Letter\n5. Bank Passbook'),

        # ── DISABILITY ────────────────────────────────────────────────────
        ('Deendayal Disabled Rehabilitation Scheme',
         'Financial assistance for NGOs providing services to persons with disabilities.',
         'The scheme provides grants to NGOs for establishing and running various projects for persons with disabilities including early intervention, special schools, vocational training, community based rehabilitation, etc.',
         'If you have a disability, this scheme connects you to funded rehabilitation programs, special education, vocational training, and support services near you.',
         'https://disabilityaffairs.gov.in/content/page/schemes.php',
         '["ALL"]', 0, 100, '[]', '[]', 1, '[]', '[]', 8,
         '1. Aadhar Card\n2. Disability Certificate (UDID)\n3. Income Certificate\n4. Passport Photo'),

        ('National Handicapped Finance & Development Corporation (NHFDC)',
         'Concessional loans and microfinance for persons with disabilities to start businesses.',
         'NHFDC provides loans at concessional rates to persons with disabilities for starting self-employment ventures, pursuing higher education, or vocational training. Loans range from Rs.25,000 to Rs.30 lakh depending on the purpose.',
         'If you have a disability and want to start a business or pursue education, NHFDC provides affordable loans with low interest rates specifically designed for you.',
         'https://nhfdc.nic.in',
         '["ALL"]', 18, 55, '[]', '[]', 1, '[]',
         '["Unemployed", "Self-Employed", "Student"]', 8,
         '1. Aadhar Card\n2. Disability Certificate\n3. Income Certificate\n4. Business Plan\n5. Bank Passbook'),

        # ── WIDOWS / PENSION ──────────────────────────────────────────────
        ('Indira Gandhi National Widow Pension Scheme',
         'Monthly pension of Rs.300–500 for widows aged 40-79 from BPL households.',
         'Under the National Social Assistance Programme, widows aged 40–79 years from BPL households receive Rs.300/month as pension. Those aged 80 and above receive Rs.500/month. States can add a top-up to increase the total pension amount.',
         'If you are a widow from a low-income household, this scheme ensures a regular monthly income to help meet basic expenses and maintain financial dignity.',
         'https://nsap.nic.in',
         '["ALL"]', 40, 100, '["Widow"]', '[]', 0, '[]', '[]', 9,
         "1. Aadhar Card\n2. Husband's Death Certificate\n3. BPL Ration Card\n4. Bank Passbook\n5. Age Proof"),

        ('Indira Gandhi National Old Age Pension Scheme (IGNOAPS)',
         'Monthly pension for senior citizens aged 60+ from BPL families.',
         'The scheme provides monthly pension to senior citizens who are 60 years and above and belong to BPL households. Those aged 60-79 receive Rs.200/month and those aged 80+ receive Rs.500/month from central government, with state top-ups varying.',
         'If you are a senior citizen from a low-income household, IGNOAPS ensures a steady pension to cover your daily needs during old age.',
         'https://nsap.nic.in',
         '["ALL"]', 60, 100, '[]', '[]', 0, '[]', '[]', 9,
         '1. Aadhar Card\n2. Age Proof\n3. BPL Certificate\n4. Bank Passbook\n5. Passport Photo'),

        # ── SELF-EMPLOYED / ENTREPRENEURS ─────────────────────────────────
        ('PM SVANidhi (Street Vendor Loan)',
         'Micro-credit of Rs.10,000–50,000 for street vendors affected by COVID-19 to restart businesses.',
         'PM SVANidhi provides affordable working capital loans to street vendors to resume their livelihoods. Vendors who repay the loan on time are eligible for an enhanced credit limit in the next cycle. The scheme also incentivizes digital transactions.',
         'If you are a street vendor or small trader who needs working capital, PM SVANidhi offers quick micro-loans with no collateral and rewards for digital payments.',
         'https://pmsvanidhi.mohua.gov.in',
         '["ALL"]', 18, 70, '[]', '[]', 0, '[]',
         '["Self-Employed"]', 8,
         '1. Aadhar Card\n2. Vendor Certificate / Letter of Recommendation\n3. Bank Passbook\n4. Mobile Number'),

        ('National SC-ST Hub',
         'Procurement opportunities and mentoring support for SC/ST entrepreneurs in government tenders.',
         'The National SC-ST Hub provides support to SC/ST entrepreneurs to participate in public procurement. It offers mentoring, financial assistance, market access, and skill development to help SC/ST micro, small and medium enterprises succeed.',
         'If you are an SC/ST entrepreneur, this hub gives you direct access to government tender opportunities and mentoring to build a successful business.',
         'https://scsthub.in',
         '["ALL"]', 21, 65, '[]', '["SC", "ST"]', 0, '[]',
         '["Self-Employed", "Working"]', 8,
         '1. Aadhar Card\n2. Caste Certificate\n3. Business Registration\n4. Bank Passbook'),

        ('Startup India Seed Fund Scheme',
         'Seed funding support of up to Rs.20 lakh for startups to validate proof of concept.',
         'The Startup India Seed Fund Scheme (SISFS) aims to provide financial assistance to startups for proof of concept, prototype development, product trials, market entry, and commercialization. Incubators recognized by DPIIT disburse the seed fund to eligible startups.',
         'If you have a startup idea and are looking for early-stage funding, this scheme provides seed money to build your MVP and validate your business model.',
         'https://seedfund.startupindia.gov.in',
         '["ALL"]', 21, 50, '[]', '[]', 0,
         '["Graduate", "Postgraduate", "12th Pass"]',
         '["Self-Employed", "Unemployed"]', 8,
         '1. Aadhar Card\n2. Startup India Registration\n3. Business Plan\n4. PAN Card\n5. Bank Account'),

        # ── MINORITY ─────────────────────────────────────────────────────
        ('Post Matric Scholarship for Minorities',
         'Scholarship for minority students at post-matric level to pursue higher education.',
         'The scheme provides financial assistance to students belonging to notified minority communities (Muslim, Christian, Sikh, Buddhist, Zoroastrian, Jain) pursuing post-matriculation studies at recognized institutions.',
         'If you belong to a minority community and are pursuing post-10th education, this scholarship provides financial support to ensure economic hardship does not interrupt your studies.',
         'https://scholarships.gov.in',
         '["ALL"]', 15, 35, '[]', '["Minority"]', 0,
         '["10th Pass", "12th Pass", "Graduate", "Postgraduate"]',
         '["Student"]', 10,
         '1. Aadhar Card\n2. Minority Community Certificate\n3. Income Certificate\n4. Marksheet\n5. Bank Passbook'),
    ]

    c = conn.cursor()
    c.executemany('''INSERT INTO financial_schemes
        (name, description, long_description, why_chosen, official_website,
         target_states, min_age, max_age, marital_status, categories,
         disability_required, education_levels, employment_statuses, priority, documents_required)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', schemes)

    conn.commit()
    conn.close()
    print(f'Seeded {len(schemes)} financial schemes.')


if __name__ == '__main__':
    seed_scholarships()
    seed_schemes()
    print('Done! Databases reseeded successfully.')
