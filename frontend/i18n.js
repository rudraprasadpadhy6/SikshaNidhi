document.addEventListener("DOMContentLoaded", () => {
    initLanguage();
});

function initLanguage() {
    let savedLang = localStorage.getItem("sn_lang");
    let langSet = localStorage.getItem("sn_lang_set");

    if (!langSet) {
        showLanguagePopup();
    } else {
        if (!savedLang) savedLang = "en";
        // Small timeout to ensure translations dictionary is loaded
        setTimeout(() => applyTranslations(savedLang), 50);
    }
}

window.showLanguagePopup = function() {
    // Prevent duplicate overlays
    if (document.getElementById("lang-overlay")) return;

    // Create the popup modal dynamically
    const overlay = document.createElement("div");
    overlay.id = "lang-overlay";
    overlay.style.cssText = "position: fixed; inset: 0; background: rgba(9, 74, 83, 0.85); backdrop-filter: blur(8px); z-index: 999999; display: flex; align-items: center; justify-content: center;";

    const modal = document.createElement("div");
    modal.style.cssText = "background: #fff; border-radius: 20px; padding: 40px; text-align: center; max-width: 400px; width: 90%; box-shadow: 0 20px 60px rgba(0,0,0,0.4); animation: fb-slide-in 0.3s ease-out;";

    modal.innerHTML = `
        <h2 style="color: #094A53; margin-bottom: 5px; font-size: 24px;">🌐 Welcome</h2>
        <h3 style="color: #48C5B9; margin-bottom: 25px; font-size: 20px; font-weight: 600;">Choose Your Language<br><span style="font-size: 16px;">अपनी भाषा चुनें | ଆପଣଙ୍କର ଭାଷା ବାଛନ୍ତୁ</span></h3>
        <div style="display: flex; flex-direction: column; gap: 12px;">
            <button onclick="setLanguage('en')" style="padding: 14px; border-radius: 12px; border: 2px solid #e5e7eb; background: #f9fafb; font-size: 18px; font-weight: bold; cursor: pointer; color: #374151; transition: all 0.2s;">🇬🇧 English</button>
            <button onclick="setLanguage('hi')" style="padding: 14px; border-radius: 12px; border: 2px solid #e5e7eb; background: #f9fafb; font-size: 18px; font-weight: bold; cursor: pointer; color: #374151; transition: all 0.2s;">🇮🇳 हिंदी</button>
            <button onclick="setLanguage('od')" style="padding: 14px; border-radius: 12px; border: 2px solid #e5e7eb; background: #f9fafb; font-size: 18px; font-weight: bold; cursor: pointer; color: #374151; transition: all 0.2s;">🇮🇳 ଓଡ଼ିଆ</button>
        </div>
    `;

    // Add close button only if language is already set (so they can cancel out if they opened it from navbar)
    if (localStorage.getItem("sn_lang_set")) {
        const closeBtn = document.createElement("button");
        closeBtn.innerHTML = "&times;";
        closeBtn.style.cssText = "position: absolute; top: 15px; right: 20px; background: none; border: none; font-size: 24px; cursor: pointer; color: #666;";
        closeBtn.onclick = () => document.getElementById("lang-overlay").remove();
        modal.appendChild(closeBtn);
        modal.style.position = "relative";
    }

    overlay.appendChild(modal);
    document.body.appendChild(overlay);

    // Add basic hover effect
    const btns = modal.querySelectorAll('button:not([style*="absolute"])');
    btns.forEach(btn => {
        btn.onmouseover = () => { btn.style.borderColor = "#48C5B9"; btn.style.background = "rgba(72,197,185,0.1)"; btn.style.color = "#094A53"; };
        btn.onmouseout = () => { btn.style.borderColor = "#e5e7eb"; btn.style.background = "#f9fafb"; btn.style.color = "#374151"; };
    });
}

window.setLanguage = function(lang) {
    localStorage.setItem("sn_lang", lang);
    localStorage.setItem("sn_lang_set", "true");
    
    const overlay = document.getElementById("lang-overlay");
    if (overlay) overlay.remove();

    applyTranslations(lang);
    
    // Dispatch event so other scripts can know language changed
    window.dispatchEvent(new CustomEvent('languageChanged', { detail: { language: lang } }));
}

window.applyTranslations = function(lang) {
    if (typeof TRANSLATIONS === 'undefined') {
        console.warn("TRANSLATIONS dictionary not found.");
        return;
    }

    if (!TRANSLATIONS[lang]) lang = "en"; // fallback
    const dict = TRANSLATIONS[lang];

    document.querySelectorAll("[data-i18n]").forEach(el => {
        const key = el.getAttribute("data-i18n");
        if (dict[key]) {
            el.innerHTML = dict[key];
        }
    });

    document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
        const key = el.getAttribute("data-i18n-placeholder");
        if (dict[key]) {
            el.setAttribute("placeholder", dict[key]);
        }
    });
    
    document.querySelectorAll("[data-i18n-title]").forEach(el => {
        const key = el.getAttribute("data-i18n-title");
        if (dict[key]) {
             el.setAttribute("title", dict[key]);
        }
    });
}
