// frontend/config.js — Auto-detects local vs production
(function () {
  var isLocal = window.location.hostname === 'localhost' ||
                window.location.hostname === '127.0.0.1';
  var url = isLocal
    ? 'http://localhost:5000'
    : 'https://sikshanidhi.onrender.com';

  // Set both variable names used across all HTML pages
  window.API_BASE_URL = url;
  window.API_BASE     = url;
})();