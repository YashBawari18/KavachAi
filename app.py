import streamlit as st
import requests
import time
import pandas as pd
import os
from datetime import datetime
from gtts import gTTS
import base64
import re

# ── Environment Variables ─────────────────────────────────────────────────────
API_URL = os.getenv("API_URL", "http://localhost:8000")

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="KAVACH | AI Cybersecurity Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Load CSS ──────────────────────────────────────────────────────────────────
def load_css():
    with open("styles.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
try:
    load_css()
except Exception:
    pass

# ── Built-in Multilingual Dictionary ─────────────────────────────────────────
LANG_OPTIONS = {
    "🇺🇸 English": "en",
    "🇮🇳 Hindi (हिंदी)": "hi",
    "🇪🇸 Spanish (Español)": "es",
    "🇫🇷 French (Français)": "fr",
    "🇩🇪 German (Deutsch)": "de",
    "🇨🇳 Chinese (中文)": "zh",
    "🇸🇦 Arabic (عربي)": "ar"
}

LANG_DICT = {
    "en": {},
    "hi": {
        "🛡️ KAVACH": "🛡️ कवच",
        "🛡️ KAVACH — AI Cybersecurity Operations Centre": "🛡️ कवच — एआई साइबर सुरक्षा संचालन केंद्र",
        "● ONLINE  |  SCANNING ACTIVE  |  ALL SYSTEMS READY": "● ऑनलाइन | स्कैनिंग सक्रिय | सभी सिस्टम तैयार",
        "📋 Recent Threat Logs": "📋 हाल के थ्रेट लॉग",
        "No scans yet. Run your first analysis!": "अभी तक कोई स्कैन नहीं। अपना पहला विश्लेषण चलाएं!",
        "🗑️ Clear Logs": "🗑️ लॉग साफ़ करें",
        "🔍 Threat Input Module": "🔍 थ्रेट इनपुट मॉड्यूल",
        "Select what kind of content you want to analyse, paste the content or upload a file, then click RUN SECURITY ANALYSIS.": "चुनें कि आप किस सामग्री का विश्लेषण करना चाहते हैं, सामग्री पेस्ट करें या फ़ाइल अपलोड करें।",
        "Select Threat Category": "थ्रेट श्रेणी चुनें",
        "**— OR — Upload Audio, Video, or Image file for deepfake analysis:**": "**— या — डीपफेक विश्लेषण के लिए ऑडियो, वीडियो या छवि फ़ाइल अपलोड करें:**",
        "Upload Media": "मीडिया अपलोड करें",
        "Content to Analyse / Description": "विश्लेषण / विवरण के लिए सामग्री",
        "🔬 RUN SECURITY ANALYSIS": "🔬 सुरक्षा विश्लेषण चलाएं",
        "⚠️ Please paste some content or upload a file first.": "⚠️ कृपया पहले कुछ सामग्री पेस्ट करें या फ़ाइल अपलोड करें।",
        "🔎 Analysing threat patterns — please wait...": "🔎 खतरे के पैटर्न का विश्लेषण किया जा रहा है — कृपया प्रतीक्षा करें...",
        "✅ Analysis Complete! See results on the right →": "✅ विश्लेषण पूरा हुआ! दाईं ओर परिणाम देखें →",
        "📊 Risk Assessment": "📊 जोखिम मूल्यांकन",
        "THREAT INDEX / 100": "खतरा सूचकांक / 100",
        "Threat Category": "थ्रेट श्रेणी",
        "🔎 What Was Found": "🔎 क्या पाया गया",
        "🧩 Suspicious Pattern Details": "🧩 संदिग्ध पैटर्न का विवरण",
        "📄 Full Security Report": "📄 पूर्ण सुरक्षा रिपोर्ट",
        "⬇️ DOWNLOAD FULL REPORT (TXT)": "⬇️ पूर्ण रिपोर्ट डाउनलोड करें (TXT)",
        "🛡️ Recommended Actions": "🛡️ अनुशंसित कार्रवाइयां",
        "Step": "कदम",
        "💡 Safety Tips": "💡 सुरक्षा टिप्स",
        "General protection guide enabled. Follow security best practices.": "सामान्य सुरक्षा मार्गदर्शिका सक्षम। सुरक्षा अभ्यास का पालन करें।",
        "AI Assistant": "एआई सहायक",
        "Ask me anything about cybersecurity! I can also speak to you.": "मुझसे साइबर सुरक्षा के बारे में कुछ भी पूछें! मैं आपसे बात भी कर सकता हूं।",
        "Ask about cybersecurity, threats...": "साइबर सुरक्षा, खतरों के बारे में पूछें...",
        "Hello! I am Kavach AI, your personal cybersecurity assistant. How can I protect you today?": "नमस्ते! मैं कवच एआई हूं, आपका व्यक्तिगत साइबर सुरक्षा सहायक। मैं आपकी सुरक्षा कैसे कर सकता हूं?",
    },
    "es": {
        "🛡️ KAVACH — AI Cybersecurity Operations Centre": "🛡️ KAVACH — Centro de Operaciones de Ciberseguridad de IA",
        "● ONLINE  |  SCANNING ACTIVE  |  ALL SYSTEMS READY": "● EN LÍNEA | ESCANEO ACTIVO | LISTO",
        "🔍 Threat Input Module": "🔍 Módulo de Entrada de Amenazas",
        "🔬 RUN SECURITY ANALYSIS": "🔬 EJECUTAR ANÁLISIS DE SEGURIDAD",
        "✅ Analysis Complete! See results on the right →": "✅ Análisis Completo! Ver resultados a la derecha →",
        "📊 Risk Assessment": "📊 Evaluación de Riesgos",
        "Threat Category": "Categoría de Amenaza",
        "🔎 What Was Found": "🔎 Lo que se encontró",
        "🛡️ Recommended Actions": "🛡️ Acciones Recomendadas",
        "AI Assistant": "Asistente de IA",
        "Hello! I am Kavach AI, your personal cybersecurity assistant. How can I protect you today?": "¡Hola! Soy Kavach AI, tu asistente personal de ciberseguridad. ¿Cómo puedo protegerte hoy?",
    },
    # Simplified structure to fall back to English automatically if key missing
}

@st.cache_data(show_spinner=False)
def t(text: str, target_lang: str) -> str:
    """Translates text to the target language dynamically using our internal dictionary."""
    if target_lang == "en" or not text:
        return text
        
    dict_for_lang = LANG_DICT.get(target_lang, {})
    return dict_for_lang.get(text, text) # Fall back to english/key if missing

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
with st.popover("🤖", use_container_width=False):
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
