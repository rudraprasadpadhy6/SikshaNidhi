// frontend/config.js
// Auto-detects environment:
//  - localhost / 127.0.0.1 → local Flask backend (port 5000)
//  - Vercel / mobile / any other host → Render production backend
const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const API_URL = isLocal ? "http://localhost:5000" : "https://sikshanidhi-2.onrender.com";
const API_BASE_URL = API_URL;
const API_BASE = API_URL;

window.API_URL = API_URL;
window.API_BASE_URL = API_BASE_URL;
window.API_BASE = API_BASE;

// Google OAuth 2.0 Client ID
window.GOOGLE_CLIENT_ID = "38862432617-nlfhacjd58kb8j0khv81nana2maqtoul.apps.googleusercontent.com";