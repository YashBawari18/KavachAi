import streamlit as st
import requests
import time
import pandas as pd
import os
import random
from datetime import datetime, timedelta
from gtts import gTTS
import base64
import re
from deep_translator import GoogleTranslator

# ── Environment Variables ─────────────────────────────────────────────────────
API_URL = os.getenv("API_URL", "http://localhost:8000")

# ── Logo Loading & Base64 ─────────────────────────────────────────────────────
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

try:
    LOGO_B64 = get_base64_image("logo.png")
except Exception:
    LOGO_B64 = ""

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="KAVACH | AI Cybersecurity Dashboard",
    page_icon=f"data:image/png;base64,{LOGO_B64}" if LOGO_B64 else "🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Preloader & Glitch Effect ────────────────────────────────────────────────
if "preloader_done" not in st.session_state:
    st.session_state.preloader_done = False

if not st.session_state.preloader_done:
    preloader_html = f"""
    <style>
        @keyframes preloaderFadeOut {{
            0%   {{ opacity: 1; visibility: visible; }}
            70%  {{ opacity: 1; visibility: visible; }}
            100% {{ opacity: 0; visibility: hidden; }}
        }}
        @keyframes pulse {{
            0%   {{ opacity: 0.4; transform: scale(0.95); }}
            50%  {{ opacity: 1; transform: scale(1); }}
            100% {{ opacity: 0.4; transform: scale(0.95); }}
        }}
        .kavach-preloader {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: #0a0f14; z-index: 99999999; display: flex;
            flex-direction: column; align-items: center; justify-content: center;
            animation: preloaderFadeOut 3s ease forwards;
            pointer-events: none;
        }}
    </style>
    <div class="kavach-preloader">
        <div style="position: relative; text-align: center;">
            <img src="data:image/png;base64,{LOGO_B64}" style="width: 150px; filter: drop-shadow(0 0 20px #00f0ff);">
            <div style="
                margin-top: 20px; color: #00ff41; font-family: 'Orbitron', sans-serif;
                letter-spacing: 5px; font-size: 24px; text-transform: uppercase;
                animation: pulse 1.5s infinite;
            ">Initiating KAVACH AI...</div>
        </div>
    </div>
    """
    st.markdown(preloader_html, unsafe_allow_html=True)
    st.session_state.preloader_done = True

# ── Load CSS ──────────────────────────────────────────────────────────────────
def load_css():
    with open("styles.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
try:
    load_css()
    # Hide Streamlit deploy button & top-right menu
    st.markdown("""
        <style>
            .stDeployButton, [data-testid="stToolbar"] {
                display: none !important;
            }
        </style>
    """, unsafe_allow_html=True)
    # Dynamic CSS override for the chatbot bridge icon
    if LOGO_B64:
        st.markdown(f"""
            <style>
                div[data-testid="stPopover"] button::before {{
                    background-image: url("data:image/png;base64,{LOGO_B64}") !important;
                    background-size: contain;
                    background-repeat: no-repeat;
                    background-position: center;
                }}
            </style>
        """, unsafe_allow_html=True)
except Exception:
    pass

# ── Comprehensive Multilingual Configuration ──────────────────────────────────
LANG_OPTIONS = {
    "🇺🇸 English": "en",
    "🇮🇳 Hindi (हिंदी)": "hi",
    "🇮🇳 Bengali (বাংলা)": "bn",
    "🇮🇳 Telugu (తెలుగు)": "te",
    "🇮🇳 Marathi (मराठी)": "mr",
    "🇮🇳 Tamil (தமிழ்)": "ta",
    "🇮🇳 Urdu (اردو)": "ur",
    "🇮🇳 Gujarati (ગુજરાતી)": "gu",
    "🇮🇳 Kannada (ಕನ್ನಡ)": "kn",
    "🇮🇳 Malayalam (മലയാളം)": "ml",
    "🇮🇳 Punjabi (ਪੰਜਾਬੀ)": "pa",
    "🇪🇸 Spanish (Español)": "es",
    "🇫🇷 French (Français)": "fr",
    "🇩🇪 German (Deutsch)": "de",
    "🇨🇳 Chinese Simplified (简体中文)": "zh-CN",
    "🇨🇳 Chinese Traditional (繁體中文)": "zh-TW",
    "🇯🇵 Japanese (日本語)": "ja",
    "🇷🇺 Russian (Русский)": "ru",
    "🇸🇦 Arabic (العربية)": "ar",
    "🇵🇹 Portuguese (Português)": "pt",
    "🇮🇹 Italian (Italiano)": "it",
    "🇰🇷 Korean (한국어)": "ko",
    "🇹🇷 Turkish (Türkçe)": "tr",
    "🇻🇳 Vietnamese (Tiếng Việt)": "vi",
    "🇹🇭 Thai (ไทย)": "th",
    "🇮🇩 Indonesian (Bahasa Indonesia)": "id",
    "🇲🇾 Malay (Bahasa Melayu)": "ms",
    "🇵🇭 Filipino (Tagalog)": "tl",
    "🇳🇱 Dutch (Nederlands)": "nl",
    "🇵🇱 Polish (Polski)": "pl",
    "🇸🇪 Swedish (Svenska)": "sv",
    "🇳🇴 Norwegian (Norsk)": "no",
    "🇩🇰 Danish (Dansk)": "da",
    "🇫🇮 Finnish (Suomi)": "fi",
    "🇬🇷 Greek (Ελληνικά)": "el",
    "🇨🇿 Czech (Čeština)": "cs",
    "🇭🇺 Hungarian (Magyar)": "hu",
    "🇷🇴 Romanian (Română)": "ro",
    "🇮🇱 Hebrew (עברית)": "iw",
    "🇮🇷 Persian (فارسی)": "fa",
    "🇺🇦 Ukrainian (Українська)": "uk",
    "🇰🇿 Kazakh (Қазақ тілі)": "kk",
    "🇿🇦 Afrikaans (Afrikaans)": "af",
    "🇳🇵 Nepali (नेपाली)": "ne",
    "🇱🇰 Sinhala (සිංහල)": "si",
    "🇲🇲 Burmese (မြန်မာ)": "my",
    "🇰Ｈ Khmer (ខ្មែរ)": "km",
    "🇱🇦 Lao (ลาว)": "lo"
}

@st.cache_data(show_spinner=False)
def t(text: str, target_lang: str) -> str:
    """Translates text to the target language dynamically using deep-translator."""
    if not text or target_lang == "en":
        return text
    
    try:
        # Normalize language codes that might differ between systems
        if target_lang == "zh": target_lang = "zh-CN"
        
        translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
        return translated if translated else text
    except Exception as e:
        # Fallback to key if translation fails
        return text

# ── Session State ─────────────────────────────────────────────────────────────
if "threat_logs" not in st.session_state:
    st.session_state.threat_logs = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "lang_choice" not in st.session_state:
    st.session_state.lang_choice = "🇺🇸 English"

def get_lang_code():
    return LANG_OPTIONS[st.session_state.lang_choice]

# ── Helpers ───────────────────────────────────────────────────────────────────
def tr(text: str) -> str:
    return t(text, get_lang_code())

INPUT_OPTIONS = [
    "📧 Phishing Email",
    "💬 Phishing Message (SMS / Chat)",
    "🔗 Suspicious URL",
    "🎭 Deepfake / Impersonation Media",
    "🔐 Anomalous Login / User Behavior",
    "🤖 AI-Generated Content",
    "💉 Prompt Injection",
]

BACKEND_TYPE_MAP = {
    "📧 Phishing Email":                   "email",
    "💬 Phishing Message (SMS / Chat)":    "message",
    "🔗 Suspicious URL":                   "url",
    "🎭 Deepfake / Impersonation Media":   "deepfake",
    "🔐 Anomalous Login / User Behavior":  "behavior",
    "🤖 AI-Generated Content":             "ai",
    "💉 Prompt Injection":                 "prompt",
}

def risk_colour(score: int) -> str:
    if score > 80: return "#ff2a2a"   
    elif score > 60: return "#ff9100" 
    elif score > 30: return "#ffea00" 
    else: return "#00ff41"            

def risk_label(score: int) -> str:
    if score > 80: return "🚨 CRITICAL"
    elif score > 60: return "🔴 HIGH RISK"
    elif score > 30: return "🟠 MODERATE"
    elif score > 0: return "🟡 LOW RISK"
    return "✅ SAFE"

def text_to_speech(text: str, lang_code: str):
    """Generates an embedded audio HTML string for the voice assistant."""
    try:
        # TTS works best with primary language codes without sub-regions for some languages
        tts_lang = lang_code.split('-')[0]
        tts = gTTS(text=text, lang=tts_lang, slow=False)
        tts.save("response.mp3")
        with open("response.mp3", "rb") as f:
            audio_bytes = f.read()
            b64 = base64.b64encode(audio_bytes).decode()
            return f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
    except Exception:
        return ""

def generate_bot_response(user_input: str) -> str:
    """A highly robust regex/keyword-based local cybersecurity knowledge bot."""
    txt = user_input.lower()
    if any(w in txt for w in ["password", "hacked", "breach"]):
        return "If you suspect a hack, immediately change your passwords using a different device. Enable Two-Factor Authentication (2FA) on all critical accounts, and monitor your bank statements."
    elif any(w in txt for w in ["phishing", "fake email", "link"]):
        return "Phishing attempts try to steal your credentials. Do not click links or download attachments. Always verify the sender's email address and navigate to the official website manually."
    elif any(w in txt for w in ["deepfake", "ai video", "fake voice"]):
        return "Deepfakes are highly realistic AI media. Look for unnatural blinking, mismatched lip-syncing, or a robotic tone. Verify the person's identity via another communication channel."
    elif any(w in txt for w in ["virus", "malware", "ransomware"]):
        return "Disconnect the infected device from the internet immediately to prevent spread. Run a full system scan using a trusted antivirus like Windows Defender or Malwarebytes."
    elif any(w in txt for w in ["safe", "secure"]):
        return "To stay safe: Use complex passwords, enable 2FA, keep your software updated, and never trust unexpected messages creating a false sense of urgency."
    elif any(w in txt for w in ["hello", "hi", "hey"]):
        return "Hello! I am your Kavach AI Security Assistant. How can I help secure your digital life today?"
    else:
        return "I am an AI trained specifically for cybersecurity. I can help you analyze threats, secure your accounts, and identify phishing or deepfakes. What specific security concern do you have?"


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    if LOGO_B64:
        st.markdown(f"""
            <div style="text-align: center; margin-bottom: 20px;">
                <img src="data:image/png;base64,{LOGO_B64}" style="width: 80px; filter: drop-shadow(0 0 10px var(--neon-cyan));">
            </div>
        """, unsafe_allow_html=True)
    else:
        st.image("https://img.icons8.com/nolan/96/shield.png", width=90)
    st.title(tr("🛡️ KAVACH"))
    
    # Language Selector
    st.selectbox("🌐 Language / 🌐 भाषा", list(LANG_OPTIONS.keys()), key="lang_choice")
    st.markdown("---")
    
    st.subheader(tr("📋 Recent Threat Logs"))
    if st.session_state.threat_logs:
        df_logs = pd.DataFrame(st.session_state.threat_logs)
        st.dataframe(df_logs[["timestamp", "type", "score"]], hide_index=True)
    else:
        st.info(tr("No scans yet. Run your first analysis!"))

    st.markdown("---")
    if st.button(tr("🗑️ Clear Logs")):
        st.session_state.threat_logs = []
        st.rerun()

    st.markdown("---")
    st.caption("KAVACH AI v2.0 - Next-Gen SecOps")

# ── Main Header ───────────────────────────────────────────────────────────────
st.title(tr("🛡️ KAVACH — AI Cybersecurity Operations Centre"))
status_msg = tr("● ONLINE  |  SCANNING ACTIVE  |  ALL SYSTEMS READY")
st.markdown(
    f"<span class='scanning-text' style='font-size:16px;'>{status_msg}</span>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ── Real-Time Threat Alerts ──────────────────────────────────────────────────
REALTIME_ALERT_POOL = [
    {"severity": "CRITICAL", "icon": "🚨", "color": "#ff2a2a", "source": "Kavach Firewall",
     "msg": "Brute-force SSH attack detected from IP 185.220.101.xx — 2,400 attempts/min"},
    {"severity": "CRITICAL", "icon": "🚨", "color": "#ff2a2a", "source": "Endpoint Shield",
     "msg": "Ransomware signature (LockBit 3.0) detected on endpoint WS-FINANCE-07"},
    {"severity": "HIGH", "icon": "🔴", "color": "#ff6b35", "source": "Email Gateway",
     "msg": "Phishing campaign targeting HR department — 14 emails quarantined"},
    {"severity": "HIGH", "icon": "🔴", "color": "#ff6b35", "source": "Network Monitor",
     "msg": "Suspicious outbound traffic to C2 server 91.215.xx.xx on port 4443"},
    {"severity": "HIGH", "icon": "🔴", "color": "#ff6b35", "source": "Threat Intel Feed",
     "msg": "New zero-day exploit CVE-2026-1847 actively exploited in the wild"},
    {"severity": "MEDIUM", "icon": "🟠", "color": "#ff9100", "source": "WAF",
     "msg": "SQL injection attempt blocked on /api/v2/users endpoint"},
    {"severity": "MEDIUM", "icon": "🟠", "color": "#ff9100", "source": "Identity Guard",
     "msg": "Anomalous login from new geo-location (Lagos, NG) for user admin@corp"},
    {"severity": "MEDIUM", "icon": "🟠", "color": "#ff9100", "source": "DNS Shield",
     "msg": "DNS tunneling pattern detected — possible data exfiltration attempt"},
    {"severity": "LOW", "icon": "🟡", "color": "#ffea00", "source": "Vulnerability Scanner",
     "msg": "3 packages with known CVEs found in production Node.js dependencies"},
    {"severity": "LOW", "icon": "🟡", "color": "#ffea00", "source": "Access Control",
     "msg": "Service account svc-backup granted elevated privileges — review recommended"},
    {"severity": "CRITICAL", "icon": "🚨", "color": "#ff2a2a", "source": "DDoS Mitigation",
     "msg": "Volumetric DDoS attack detected — 12 Gbps flood targeting primary gateway"},
    {"severity": "HIGH", "icon": "🔴", "color": "#ff6b35", "source": "Deepfake Detector",
     "msg": "AI-generated voice deepfake flagged in VoIP call to finance department"},
    {"severity": "MEDIUM", "icon": "🟠", "color": "#ff9100", "source": "Cloud Monitor",
     "msg": "S3 bucket policy changed to public access — potential data exposure"},
    {"severity": "LOW", "icon": "🟡", "color": "#ffea00", "source": "Compliance Engine",
     "msg": "TLS 1.0 connection detected from legacy client — deprecation warning"},
    {"severity": "CRITICAL", "icon": "🚨", "color": "#ff2a2a", "source": "Malware Sandbox",
     "msg": "Trojan dropper detected in email attachment — SHA256 matches APT29 toolkit"},
]

def generate_realtime_alerts(n=5):
    """Generate n randomized real-time alerts with recent timestamps."""
    now = datetime.now()
    selected = random.sample(REALTIME_ALERT_POOL, min(n, len(REALTIME_ALERT_POOL)))
    alerts = []
    for i, alert in enumerate(selected):
        ts = now - timedelta(seconds=random.randint(5, 120 + i * 30))
        alerts.append({**alert, "time": ts.strftime("%H:%M:%S")})
    alerts.sort(key=lambda x: x["time"], reverse=True)
    return alerts

# Auto-refresh alerts every 8 seconds
if "alert_tick" not in st.session_state:
    st.session_state.alert_tick = 0
if "realtime_alerts" not in st.session_state or time.time() - st.session_state.get("alert_last_refresh", 0) > 8:
    st.session_state.realtime_alerts = generate_realtime_alerts(5)
    st.session_state.alert_last_refresh = time.time()

alerts = st.session_state.realtime_alerts

alerts_container = st.container()
with alerts_container:
    st.subheader(tr("🔔 Real-Time Threat Alerts"))
    
    # Build the alerts HTML
    alerts_html = '<div style="display:flex; flex-direction:column; gap:10px; margin-bottom:20px;">'
    for a in alerts:
        alerts_html += f"""<div style="background:rgba(10,15,25,0.85);border-left:4px solid {a['color']};border-radius:8px;padding:12px 18px;display:flex;align-items:center;gap:14px;box-shadow:0 2px 12px rgba(0,0,0,0.4);animation:alertSlideIn 0.5s ease;"><div style="font-size:28px; min-width:36px; text-align:center;">{a['icon']}</div><div style="flex:1;"><div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;"><span style="color:{a['color']}; font-weight:800; font-size:13px; font-family:'Orbitron',sans-serif; letter-spacing:2px;">{a['severity']}</span><span style="color:#586069; font-size:12px; font-family:'Rajdhani',sans-serif;">🕐 {a['time']}  •  {a['source']}</span></div><div style="color:#c9d1d9; font-size:14px; font-family:'Rajdhani',sans-serif; line-height:1.4;">{tr(a['msg'])}</div></div></div>"""
    alerts_html += "</div>"
    alerts_html += """
    <style>
        @keyframes alertSlideIn {
            from { opacity: 0; transform: translateX(-20px); }
            to   { opacity: 1; transform: translateX(0); }
        }
    </style>
    """
    st.markdown(alerts_html, unsafe_allow_html=True)

# Refresh button
col_refresh, col_spacer = st.columns([1, 5])
with col_refresh:
    if st.button(tr("🔄 Refresh Alerts")):
        st.session_state.realtime_alerts = generate_realtime_alerts(5)
        st.session_state.alert_last_refresh = time.time()
        st.rerun()

st.markdown("---")

# ── Layout ────────────────────────────────────────────────────────────────────
col_input, col_result = st.columns([2, 1])

with col_input:
    st.subheader(tr("🔍 Threat Input Module"))
    st.caption(tr("Select what kind of content you want to analyse, paste the content or upload a file, then click RUN SECURITY ANALYSIS."))

    # Note: We don't translate the options here to preserve backend mapping, but we translate the display
    translated_options = {opt: tr(opt) for opt in INPUT_OPTIONS}
    display_to_real = {v: k for k, v in translated_options.items()}
    
    selected_display = st.selectbox(tr("Select Threat Category"), list(translated_options.values()))
    input_type = display_to_real[selected_display]
    
    # File Uploader
    uploaded_file = None
    if input_type == "🎭 Deepfake / Impersonation Media":
        st.markdown(tr("**— OR — Upload Audio, Video, or Image file for deepfake analysis:**"))
        uploaded_file = st.file_uploader(tr("Upload Media"), type=["mp4", "mkv", "avi", "mov", "mp3", "wav", "m4a", "aac", "ogg", "jpg", "jpeg", "png", "webp", "heic"])

    user_input = st.text_area(
        tr("Content to Analyse / Description"),
        height=160 if input_type == "🎭 Deepfake / Impersonation Media" else 200,
    )

    run_btn = st.button(tr("🔬 RUN SECURITY ANALYSIS"), use_container_width=True)

    if run_btn:
        if not user_input.strip() and uploaded_file is None:
            st.warning(tr("⚠️ Please paste some content or upload a file first."))
        else:
            with st.spinner(tr("🔎 Analysing threat patterns — please wait...")):
                time.sleep(1.5)
                try:
                    is_file_upload = uploaded_file is not None

                    if is_file_upload:
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        data_payload = {"content_type": BACKEND_TYPE_MAP[input_type]}
                        response = requests.post(f"{API_URL}/detect-file", data=data_payload, files=files, timeout=45)
                    else:
                        payload = {"content": user_input, "content_type": BACKEND_TYPE_MAP[input_type]}
                        response = requests.post(f"{API_URL}/detect", json=payload, timeout=15)

                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.last_result = data
                        st.session_state.last_input_label = input_type
                        
                        log_type = data["threat_type"]
                        if is_file_upload:
                            log_type += " (File)"

                        st.session_state.threat_logs.append({
                            "timestamp": datetime.now().strftime("%H:%M:%S"),
                            "type": log_type,
                            "score": data["risk_score"],
                        })
                        st.success(tr("✅ Analysis Complete! See results on the right →"))
                    else:
                        st.error(f"Backend Error: {response.text}")
                except Exception as e:
                    st.error(f"Error connecting to KavachAI Core: {e}")

# ── Results & Features ───────────────────────────────────────────────────────
if "last_result" in st.session_state:
    result = st.session_state.last_result
    score = result["risk_score"]
    colour = risk_colour(score)
    label = tr(risk_label(score))

    with col_result:
        st.subheader(tr("📊 Risk Assessment"))
        st.markdown(
            f"""
            <div class="risk-meter-container">
                <div style="font-size:70px; font-weight:900; color:{colour}; font-family:'Orbitron', sans-serif; text-shadow: 0 0 20px {colour};">{score}</div>
                <div style="font-size:14px; color:#8b949e; letter-spacing:3px; margin-top:5px; font-weight:bold;">{tr('THREAT INDEX / 100')}</div>
                <div style="font-size:24px; margin-top:15px; font-weight:700; color:{colour}; text-shadow: 0 0 10px {colour};">{label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        cat_lbl = tr('Threat Category')
        cat_val = tr(result['threat_type'])
        st.markdown(f"<br>**{cat_lbl}:** `{cat_val}`", unsafe_allow_html=True)
        st.markdown("---")

        st.subheader(tr("🔎 What Was Found"))
        for expl in result["explanation"]:
            st.warning(tr(expl))

        if result["detected_patterns"]:
            with st.expander(tr("🧩 Suspicious Pattern Details")):
                for p in result["detected_patterns"]:
                    st.code(tr(p))
                    
        # --- ALERT SOUND INJECTION ---
        if score > 60:
            audio_url = "https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg"
            st.markdown(
                f"""
                <audio autoplay>
                    <source src="{audio_url}" type="audio/ogg">
                </audio>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    tab_report, tab_actions, tab_tips = st.tabs([
        tr("📄 Full Security Report"), tr("🛡️ Recommended Actions"), tr("💡 Safety Tips")
    ])

    with tab_report:
        full_report = result.get("full_report", "")
        if full_report:
            # Dynamically translate the entire generated report
            translated_report = tr(full_report)
            st.text_area("", translated_report, height=400, key="report_area")
            fname = f"Kavach_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            st.download_button(label=tr("⬇️ DOWNLOAD FULL REPORT (TXT)"), data=translated_report, file_name=fname, mime="text/plain", use_container_width=True)

    with tab_actions:
        recs = result.get("recommendations", [])
        if recs:
            for i, rec in enumerate(recs, 1):
                action = rec["action"] if isinstance(rec, dict) else rec.action
                desc   = rec["description"] if isinstance(rec, dict) else rec.description
                st.markdown(
                    f"""
                    <div style="background:rgba(20,25,35,0.8); border-left:4px solid {colour};
                                border-radius:6px; padding:20px; margin-bottom:15px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                        <div style="color:{colour}; font-weight:700; font-size:18px; font-family:'Orbitron', sans-serif;">
                            {tr('Step')} {i}. {tr(action)}
                        </div>
                        <div style="color:#c9d1d9; font-size:15px; margin-top:10px; font-family:'Rajdhani', sans-serif;">
                            {tr(desc)}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with tab_tips:
        st.info(tr("General protection guide enabled. Follow security best practices."))
        st.write(tr("1. 🔑 **Use Strong Passwords**: Avoid dictionary words. Use a manager."))
        st.write(tr("2. 📱 **Enable 2FA**: Always use two-factor authentication."))
        st.write(tr("3. 🔗 **Don't Click Suspicious Links**: Type the URL manually."))
        st.write(tr("4. 🎬 **Verify Senders**: Call the person if an email/video asks for money."))

else:
    with col_result:
        st.info("👈 " + tr("Select what kind of content you want to analyse, paste the content or upload a file, then click RUN SECURITY ANALYSIS."))


# ── FLOATING CHATBOT (Bottom Right Voice Assistant) ───────────────────────────
# We use an empty string as popover label because we'll style the button via CSS background
with st.popover(" ", use_container_width=False):
    st.markdown(f"### 🛡️ Kavach {tr('AI Assistant')}")
    st.caption(tr("Ask me anything about cybersecurity! I can also speak to you."))
    
    if not st.session_state.chat_history:
        st.session_state.chat_history.append({"role": "assistant", "content": "Hello! I am Kavach AI, your personal cybersecurity assistant. How can I protect you today?"})

    chat_container = st.container(height=300)
    
    with chat_container:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"], avatar="🛡️" if msg["role"] == "assistant" else "👤"):
                st.write(tr(msg["content"]))
                
    # Always play the audio for the latest assistant message if it was just generated
    if st.session_state.chat_history[-1]["role"] == "assistant" and len(st.session_state.chat_history) > 1:
        latest_reply = tr(st.session_state.chat_history[-1]["content"])
        audio_html = text_to_speech(latest_reply, get_lang_code())
        st.markdown(audio_html, unsafe_allow_html=True)

    chat_input = st.chat_input(tr("Ask about cybersecurity, threats..."))
    if chat_input:
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": chat_input})
        
        # Generate and add response
        reply = generate_bot_response(chat_input)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"<div style='text-align: center; color: #8b949e;'>Kavach AI v2.0 | Real-time Cybersecurity Intelligence | Stay safe online.</div>", unsafe_allow_html=True)
