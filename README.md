# 🎓 SikshaNidhi — Empowering Every Student

SikshaNidhi is an AI-powered educational assistant and scholarship discovery platform built for students across India. It helps users find scholarships, financial schemes, and provides mental wellness support through PixaBot — all running completely **database-free** with an in-memory engine.

---

## 🚀 Project Structure

```
APPATHON/
├── backend/                  # Python Flask Backend (API)
│   ├── main.py               # 🌟 Main unified server — all API routes
│   ├── run_servers.py        # 🚀 Local dev launcher (backend + frontend)
│   ├── requirements.txt      # Python dependencies
│   ├── .env                  # Secrets (GROQ_API_KEY, ADMIN_FEEDBACK_KEY)
│   └── .env.example          # Template for environment variables
│
├── frontend/                 # Static HTML/CSS/JS Frontend
│   ├── login.html            # 🔐 Login page
│   ├── dashboard.html        # 📊 Main dashboard
│   ├── index1.html           # 🎓 Scholarship Finder (Scholar)
│   ├── index2.html           # 💰 Financial Scheme Finder (Capital)
│   ├── PixaBot.html          # 🤖 AI Chatbot (PixaBot)
│   ├── feedback_admin.html   # 🛡️ Admin Feedback Panel
│   ├── config.js             # API URL configuration
│   ├── translations.js       # Multi-language translations
│   ├── i18n.js               # Internationalization logic
│   └── styles.css            # Global styles
│
├── api/
│   └── index.py              # Vercel Serverless API handlers
│
├── vercel.json               # Vercel deployment configuration
├── Procfile                  # Render/Heroku deployment config
└── requirements.txt          # Root-level Python dependencies
```

---

## ⚡ Quick Start (Local Development)

### 1. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 2. Configure Environment

Copy and fill in your keys:
```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:
```env
GROQ_API_KEY=your_groq_api_key_here
ADMIN_FEEDBACK_KEY=your_custom_admin_key
```

### 3. Run the Project

**Option A — Run everything with one command:**
```bash
python backend/run_servers.py
```

**Option B — Run servers individually:**
```bash
# Terminal 1: Backend API
python backend/main.py

# Terminal 2: Frontend
python -m http.server 3000 --directory frontend
```

Open your browser: **http://localhost:3000/login.html**

---

## 🛡️ Admin Panel

Access the Feedback Admin Panel at:
```
http://localhost:3000/feedback_admin.html
```
Use the `ADMIN_FEEDBACK_KEY` you set in `.env` to log in.

---

## 🤖 Features

| Feature | Description |
|---|---|
| 🎓 Scholar | Search & filter scholarships by age, gender, caste, marks, income |
| 💰 Capital | Match government financial schemes to your profile |
| 🤖 PixaBot | AI chat advisor (Groq/Llama 3.1) with voice & multilingual support |
| 🧠 Therapy Mode | Emotional support mode within PixaBot |
| 📬 Feedback | Users can leave feedback; admins can view, manage, and export |

---

## ☁️ Deployment

### Vercel (Frontend + API)
Push to GitHub and import into Vercel. Set environment variables in the Vercel dashboard.

### Render/Railway (Backend)
The `Procfile` is already configured:
```
web: cd backend && gunicorn main:app
```

---

## 🔧 Tech Stack

- **Backend**: Python, Flask, Flask-CORS
- **AI**: Groq API (Llama 3.1 8B Instant)
- **TTS**: Edge-TTS (Multi-lingual voice support)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Data**: In-memory (no database required)
