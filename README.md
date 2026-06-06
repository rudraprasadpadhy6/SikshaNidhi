# ShikshaNidhi (APPATHON)

ShikshaNidhi is an innovative educational financial aid portal and intelligence platform. It enables students and users to easily discover scholarships, explore financial schemes, and interact with an AI educational advisor/therapist.

## 🚀 Key Features

- **Scholarship Portal (`/scholar`):** Search and filter government and private scholarships based on age, gender, caste, income, and marks. Track live and upcoming scholarships easily.
- **Financial Schemes (`/capital`):** Discover state and central financial schemes tailored to your marital status, education level, employment status, category, and disability status.
- **PixaBot AI (`/pixa`):** An interactive educational advisor and empathetic personal therapist powered by Groq AI (Llama 3.1) and Edge TTS for voice responses. It supports multiple languages (English, Hindi, Odia) and can fetch scholarship data directly in the chat.
- **Admin Dashboard & Feedback System (`/admin`):** A secure feedback mechanism where users can rate and review their experience, and administrators can view, manage, and export feedback as CSV.
- **Multilingual Support:** The application is fully internationalized (i18n), allowing users to switch languages easily via `translations.js`.

## 💻 Tech Stack

### Frontend
- HTML5, CSS3, JavaScript (Vanilla)
- Custom Internationalization System (`i18n.js`)

### Backend
- **Python & Flask:** Core API handling endpoints.
- **SQLite:** Lightweight local databases for scholarships (`scholarships.db`), schemes (`schemes.db`), and user feedback.
- **Groq API (Llama-3.1-8b):** Fast AI inference engine for PixaBot's intelligence.
- **edge-tts:** Text-to-speech generation for PixaBot's voice responses.
- **Vercel:** Serverless deployment using `vercel.json` and the consolidated `api/index.py` serverless function.

## 📂 Project Structure

- `/frontend/` - Contains all frontend assets, including HTML pages (`dashboard.html`, `index1.html`, `PixaBot.html`, `feedback_admin.html`), CSS, and JavaScript.
- `/backend/` - Contains backend python scripts, microservices, database schemas, and the SQLite `.db` files located inside `/backend/data/`.
- `/api/` - Vercel serverless entry point (`index.py`), which consolidates the Flask application for production.
- `vercel.json` - Configuration for URL rewriting and serverless deployment on Vercel.

## ⚙️ How to Run Locally

### Prerequisites
- Python 3.8+
- A [Groq API Key](https://console.groq.com/) for PixaBot

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd APPATHON
   ```

2. **Set up the Python Environment:**
   Create a virtual environment and install dependencies.
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a `.env` file in the root directory with the following variables:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ADMIN_FEEDBACK_KEY=siksha-admin-2026
   ```

4. **Run the Backend:**
   Run the consolidated API server locally.
   ```bash
   export FLASK_APP=api/index.py
   flask run --port 5000
   ```

5. **Run the Frontend:**
   Use any local web server to serve the `frontend` folder.
   ```bash
   cd frontend
   python -m http.server 3000
   ```
   Open your browser and navigate to `http://localhost:3000`.

## 🛡️ Security & Administration
- The Admin dashboard (`/admin`) is protected by a custom `ADMIN_FEEDBACK_KEY`. Ensure this key is kept secret and configured correctly in your deployment environment variables to prevent unauthorized access to user feedback data.
