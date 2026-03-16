import streamlit as st
import requests
import time
import pandas as pd
from datetime import datetime

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

# ── Multilingual Dictionary ───────────────────────────────────────────────────
LANG_DICT = {
    "English": {
        "title": "🛡️ KAVACH — AI Cybersecurity Operations Centre",
        "status": "● ONLINE &nbsp;|&nbsp; SCANNING ACTIVE &nbsp;|&nbsp; ALL SYSTEMS READY",
        "sidebar_title": "🛡️ KAVACH",
        "recent_logs": "📋 Recent Threat Logs",
        "clear_logs": "🗑️ Clear Logs",
        "no_scans": "No scans yet. Run your first analysis!",
        "input_module": "🔍 Threat Input Module",
        "input_caption": "Select what kind of content you want to analyse, paste the content or upload a file, then click **RUN SECURITY ANALYSIS**.",
        "select_category": "Select Threat Category",
        "upload_opt": "**(Optional) Upload Audio, Video, or Image file for deepfake analysis:**",
        "upload_btn": "Upload Media",
        "paste_desc": "*Or paste a description/transcript below:*",
        "content_label": "Content to Analyse / Description",
        "run_btn": "🔬 RUN SECURITY ANALYSIS",
        "warning_empty": "⚠️  Please paste some content or upload a file first.",
        "analyzing": "🔎 Analysing threat patterns — please wait...",
        "success": "✅ Analysis Complete! See results on the right →",
        "risk_assessment": "📊 Risk Assessment",
        "what_was_found": "🔎 What Was Found",
        "pattern_details": "🧩 Suspicious Pattern Details",
        "tab_report": "📄 Full Security Report",
        "tab_actions": "🛡️ Recommended Actions",
        "tab_tips": "💡 Safety Tips",
        "tab_chat": "💬 AI Security Assistant",
        "dl_report": "⬇️ DOWNLOAD FULL REPORT (TXT)",
        "chat_welcome": "Hello! I am Kavach AI, your personal cybersecurity assistant. How can I protect you today?",
        "chat_placeholder": "Ask about cybersecurity, threats, or protection...",
        "footer": "Kavach AI v2.0 | Real-time Cybersecurity Intelligence | Stay safe online.",
    },
    "Hindi": {
        "title": "🛡️ KAVACH — एआई साइबर सुरक्षा संचालन केंद्र",
        "status": "● ऑनलाइन &nbsp;|&nbsp; स्कैनिंग सक्रिय &nbsp;|&nbsp; सभी सिस्टम तैयार",
        "sidebar_title": "🛡️ कवच",
        "recent_logs": "📋 हाल के थ्रेट लॉग",
        "clear_logs": "🗑️ लॉग साफ़ करें",
        "no_scans": "अभी तक कोई स्कैन नहीं। अपना पहला विश्लेषण चलाएं!",
        "input_module": "🔍 थ्रेट इनपुट मॉड्यूल",
        "input_caption": "चुनें कि आप किस सामग्री का विश्लेषण करना चाहते हैं, सामग्री पेस्ट करें या फ़ाइल अपलोड करें, फिर **सुरक्षा विश्लेषण चलाएं** पर क्लिक करें।",
        "select_category": "थ्रेट श्रेणी चुनें",
        "upload_opt": "**(वैकल्पिक) डीपफेक विश्लेषण के लिए ऑडियो, वीडियो या चित्र फ़ाइल अपलोड करें:**",
        "upload_btn": "मीडिया अपलोड करें",
        "paste_desc": "*या नीचे विवरण/ट्रांसक्रिप्ट पेस्ट करें:*",
        "content_label": "विश्लेषण / विवरण के लिए सामग्री",
        "run_btn": "🔬 सुरक्षा विश्लेषण चलाएं",
        "warning_empty": "⚠️  कृपया पहले कुछ सामग्री पेस्ट करें या फ़ाइल अपलोड करें।",
        "analyzing": "🔎 खतरे के पैटर्न का विश्लेषण किया जा रहा है — कृपया प्रतीक्षा करें...",
        "success": "✅ विश्लेषण पूरा हुआ! दाईं ओर परिणाम देखें →",
        "risk_assessment": "📊 जोखिम मूल्यांकन",
        "what_was_found": "🔎 क्या पाया गया",
        "pattern_details": "🧩 संदिग्ध पैटर्न का विवरण",
        "tab_report": "📄 पूर्ण सुरक्षा रिपोर्ट",
        "tab_actions": "🛡️ अनुशंसित कार्रवाइयां",
        "tab_tips": "💡 सुरक्षा टिप्स",
        "tab_chat": "💬 एआई सुरक्षा सहायक",
        "dl_report": "⬇️ पूर्ण रिपोर्ट डाउनलोड करें (TXT)",
        "chat_welcome": "नमस्ते! मैं कवच एआई हूं, आपका व्यक्तिगत साइबर सुरक्षा सहायक। मैं आपकी सुरक्षा कैसे कर सकता हूं?",
        "chat_placeholder": "साइबर सुरक्षा, खतरों या बचाव के बारे में पूछें...",
        "footer": "कवच एआई v2.0 | रीयल-टाइम साइबर सुरक्षा इंटेलिजेंस | ऑनलाइन सुरक्षित रहें।",
    }
}

# ── Session State ─────────────────────────────────────────────────────────────
if "threat_logs" not in st.session_state:
    st.session_state.threat_logs = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "lang" not in st.session_state:
    st.session_state.lang = "English"

# ── Helpers ───────────────────────────────────────────────────────────────────
def t(key):
    return LANG_DICT[st.session_state.lang].get(key, key)

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
    if score > 80: return "#ff2a2a"   # critical neon red
    elif score > 60: return "#ff9100"   # high orange
    elif score > 30: return "#ffea00"   # moderate neon yellow
    else: return "#00ff41"              # safe neon green

def risk_label(score: int) -> str:
    if score > 80: return "🚨 CRITICAL"
    elif score > 60: return "🔴 HIGH RISK"
    elif score > 30: return "🟠 MODERATE"
    elif score > 0: return "🟡 LOW RISK"
    return "✅ SAFE"

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/nolan/96/shield.png", width=90) # Cooler glowing icon
    st.title(t("sidebar_title"))
    
    st.selectbox("🌐 Language / भाषा", ["English", "Hindi"], key="lang")
    st.markdown("---")
    
    st.subheader(t("recent_logs"))
    if st.session_state.threat_logs:
        df_logs = pd.DataFrame(st.session_state.threat_logs)
        st.dataframe(df_logs[["timestamp", "type", "score"]], hide_index=True)
    else:
        st.info(t("no_scans"))

    st.markdown("---")
    if st.button(t("clear_logs")):
        st.session_state.threat_logs = []
        st.rerun()

    st.markdown("---")
    st.caption("KAVACH AI v2.0 - Next-Gen SecOps")

# ── Main Header ───────────────────────────────────────────────────────────────
st.title(t("title"))
st.markdown(
    f"<span class='scanning-text' style='font-size:16px;'>{t('status')}</span>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ── Layout ────────────────────────────────────────────────────────────────────
col_input, col_result = st.columns([2, 1])

with col_input:
    st.subheader(t("input_module"))
    st.caption(t("input_caption"))

    input_type = st.selectbox(t("select_category"), INPUT_OPTIONS)
    
    # File Uploader
    uploaded_file = None
    if input_type == "🎭 Deepfake / Impersonation Media":
        st.markdown(t("upload_opt"))
        uploaded_file = st.file_uploader(t("upload_btn"), type=["mp4", "mkv", "avi", "mov", "mp3", "wav", "m4a", "aac", "ogg", "jpg", "jpeg", "png", "webp", "heic"])
        st.markdown(t("paste_desc"))

    user_input = st.text_area(
        t("content_label"),
        height=160 if input_type == "🎭 Deepfake / Impersonation Media" else 200,
    )

    run_btn = st.button(t("run_btn"), use_container_width=True)

    if run_btn:
        if not user_input.strip() and uploaded_file is None:
            st.warning(t("warning_empty"))
        else:
            with st.spinner(t("analyzing")):
                time.sleep(1.5)
                try:
                    is_file_upload = uploaded_file is not None

                    if is_file_upload:
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        data_payload = {"content_type": BACKEND_TYPE_MAP[input_type]}
                        response = requests.post("http://localhost:8000/detect-file", data=data_payload, files=files, timeout=45)
                    else:
                        payload = {"content": user_input, "content_type": BACKEND_TYPE_MAP[input_type]}
                        response = requests.post("http://localhost:8000/detect", json=payload, timeout=15)

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
                        st.success(t("success"))
                    else:
                        st.error(f"Backend Error: {response.text}")
                except Exception as e:
                    st.error(f"Error connecting to KavachAI Core: {e}")

# ── Results & Features ───────────────────────────────────────────────────────
if "last_result" in st.session_state:
    result = st.session_state.last_result
    score = result["risk_score"]
    colour = risk_colour(score)
    label = risk_label(score)

    with col_result:
        st.subheader(t("risk_assessment"))
        st.markdown(
            f"""
            <div class="risk-meter-container">
                <div style="font-size:70px; font-weight:900; color:{colour}; font-family:'Orbitron', sans-serif; text-shadow: 0 0 20px {colour};">{score}</div>
                <div style="font-size:14px; color:#8b949e; letter-spacing:3px; margin-top:5px; font-weight:bold;">THREAT INDEX / 100</div>
                <div style="font-size:24px; margin-top:15px; font-weight:700; color:{colour}; text-shadow: 0 0 10px {colour};">{label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(f"<br>**Threat Category:** `{result['threat_type']}`", unsafe_allow_html=True)
        st.markdown("---")

        st.subheader(t("what_was_found"))
        for expl in result["explanation"]:
            st.warning(expl)

        if result["detected_patterns"]:
            with st.expander(t("pattern_details")):
                for p in result["detected_patterns"]:
                    st.code(p)
                    
        # --- ALERT SOUND INJECTION ---
        if score > 60:
            # Play a loud alarm sound automatically if high risk
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

    tab_report, tab_actions, tab_chat, tab_tips = st.tabs([
        t("tab_report"), t("tab_actions"), t("tab_chat"), t("tab_tips")
    ])

    with tab_report:
        full_report = result.get("full_report", "")
        if full_report:
            st.text_area("", full_report, height=400, key="report_area")
            fname = f"Kavach_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            st.download_button(label=t("dl_report"), data=full_report, file_name=fname, mime="text/plain", use_container_width=True)

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
                            Step {i}. {action}
                        </div>
                        <div style="color:#c9d1d9; font-size:15px; margin-top:10px; font-family:'Rajdhani', sans-serif;">
                            {desc}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with tab_chat:
        st.caption("AI Security Analyst Chatbot - Ask follow-up questions about this threat.")
        
        # Initialize internal chat if empty
        if not st.session_state.chat_history:
            st.session_state.chat_history.append({"role": "assistant", "content": t("chat_welcome")})

        for msg in st.session_state.chat_history[-4:]: # show last 4 messages to save space
            with st.chat_message(msg["role"], avatar="🛡️" if msg["role"] == "assistant" else "👤"):
                st.write(msg["content"])

        chat_input = st.chat_input(t("chat_placeholder"))
        if chat_input:
            st.session_state.chat_history.append({"role": "user", "content": chat_input})
            st.rerun() # Refresh to show user msg
            
        # Very simple mock response generation based on latest user input
        if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "user":
            user_msg = st.session_state.chat_history[-1]["content"].lower()
            with st.spinner("Kavach AI is typing..."):
                time.sleep(1)
                reply = "I'm analyzing your query. As an AI assistant, I recommend referring to the 'Recommended Actions' tab for immediate steps."
                if "what" in user_msg and "do" in user_msg:
                    reply = "You should immediately change your passwords and enable Two-Factor Authentication!"
                elif "safe" in user_msg:
                    reply = "If the risk score is below 30, it's generally safe, but always remain cautious online."
                elif "thanks" in user_msg or "help" in user_msg:
                    reply = "You're welcome! My primary directive is to ensure your digital safety."
                
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
                st.rerun()

    with tab_tips:
        st.info("General protection guide enabled. Follow security best practices.")
        # Basic static tips for demo
        st.write("1. 🔑 **Use Strong Passwords**: Avoid dictionary words. Use a manager.")
        st.write("2. 📱 **Enable 2FA**: Always use two-factor authentication.")
        st.write("3. 🔗 **Don't Click Suspicious Links**: Type the URL manually.")
        st.write("4. 🎬 **Verify Senders**: Call the person if an email/video asks for money.")

else:
    with col_result:
        st.info("👈 " + t("input_caption"))

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"<div style='text-align: center; color: #8b949e;'>{t('footer')}</div>", unsafe_allow_html=True)
