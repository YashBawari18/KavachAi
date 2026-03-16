import streamlit as st
import requests
import time
import pandas as pd
from datetime import datetime

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="KAVACH | AI Cybersecurity Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# ── Load CSS ──────────────────────────────────────────────────────────────────
def load_css():
    with open("styles.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

try:
    load_css()
except Exception:
    pass

# ── Session State ─────────────────────────────────────────────────────────────
if "threat_logs" not in st.session_state:
    st.session_state.threat_logs = []

# ── Input type ↔ backend type mapping ────────────────────────────────────────
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

PLACEHOLDER_MAP = {
    "📧 Phishing Email":
        "Paste the full email text here, including subject, body, and any links you received...",
    "💬 Phishing Message (SMS / Chat)":
        "Paste the SMS or chat message here, including any links or unusual requests...",
    "🔗 Suspicious URL":
        "Paste the full URL here (e.g. https://suspicious-site.xyz/login-verify)...",
    "🎭 Deepfake / Impersonation Media":
        "Describe the video/audio or paste any metadata / transcript here (e.g. 'CEO voice clone asking to wire funds, lip sync looks off...')",
    "🔐 Anomalous Login / User Behavior":
        "Describe the suspicious activity (e.g. 'Login from Russia at 3am. Password changed. MFA disabled.')...",
    "🤖 AI-Generated Content":
        "Paste the AI-generated text or describe the suspicious content here...",
    "💉 Prompt Injection":
        "Paste the user prompt or AI input that looks suspicious here...",
}

# ── Risk colour helper ────────────────────────────────────────────────────────
def risk_colour(score: int) -> str:
    if score > 80:
        return "#ff1744"   # critical – red
    elif score > 60:
        return "#ff6d00"   # high – deep orange
    elif score > 30:
        return "#ffd600"   # moderate – amber
    else:
        return "#00e676"   # safe – green


def risk_label(score: int) -> str:
    if score > 80:
        return "🚨 CRITICAL"
    elif score > 60:
        return "🔴 HIGH RISK"
    elif score > 30:
        return "🟠 MODERATE"
    elif score > 0:
        return "🟡 LOW RISK"
    return "✅ SAFE"


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/neon/96/shield.png", width=80)
    st.title("🛡️ KAVACH")
    st.markdown("---")
    st.subheader("📋 Recent Threat Logs")
    if st.session_state.threat_logs:
        df_logs = pd.DataFrame(st.session_state.threat_logs)
        st.dataframe(df_logs[["timestamp", "type", "score"]], hide_index=True)
    else:
        st.info("No scans yet. Run your first analysis!")

    st.markdown("---")
    if st.button("🗑️ Clear Logs"):
        st.session_state.threat_logs = []
        st.rerun()

    st.markdown("---")
    st.caption("KAVACH AI v2.0\nReal-time Cybersecurity Intelligence")

# ── Main Header ───────────────────────────────────────────────────────────────
st.title("🛡️ KAVACH — AI Cybersecurity Operations Centre")
st.markdown(
    "<span style='color:#00ff41; font-size:14px;'>● ONLINE &nbsp;|&nbsp; SCANNING ACTIVE &nbsp;|&nbsp; ALL SYSTEMS READY</span>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ── Layout ────────────────────────────────────────────────────────────────────
col_input, col_result = st.columns([2, 1])

with col_input:
    st.subheader("🔍 Threat Input Module")
    st.caption("Select what kind of content you want to analyse, paste the content or upload a file, then click **RUN SECURITY ANALYSIS**.")

    input_type = st.selectbox("Select Threat Category", INPUT_OPTIONS)
    
    # Optional File Uploader for Deepfake Media
    uploaded_file = None
    if input_type == "🎭 Deepfake / Impersonation Media":
        st.markdown("**(Optional) Upload Audio, Video, or Image file for deepfake analysis:**")
        uploaded_file = st.file_uploader("Upload Media (mp4, mp3, wav, jpg, png, etc.)", type=["mp4", "mkv", "avi", "mov", "mp3", "wav", "m4a", "aac", "ogg", "jpg", "jpeg", "png", "webp", "heic"])
        st.markdown("*Or paste a description/transcript below:*")

    user_input = st.text_area(
        f"Content to Analyse / Description",
        placeholder=PLACEHOLDER_MAP.get(input_type, "Paste content here..."),
        height=180 if input_type == "🎭 Deepfake / Impersonation Media" else 220,
    )

    run_btn = st.button("🔬 RUN SECURITY ANALYSIS", use_container_width=True)

    if run_btn:
        if not user_input.strip() and uploaded_file is None:
            st.warning("⚠️  Please paste some content or upload a file before running the analysis.")
        else:
            with st.spinner("🔎 Analysing threat patterns — please wait..."):
                time.sleep(1.5)
                try:
                    is_file_upload = uploaded_file is not None

                    if is_file_upload:
                        # Send to /detect-file
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        data_payload = {"content_type": BACKEND_TYPE_MAP[input_type]}
                        response = requests.post("http://localhost:8000/detect-file", data=data_payload, files=files, timeout=45)
                    else:
                        # Standard text /detect
                        payload = {
                            "content": user_input,
                            "content_type": BACKEND_TYPE_MAP[input_type],
                        }
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
                        st.success("✅ Analysis Complete! See results on the right →")
                    else:
                        st.error(f"Backend Error: {response.text}")
                except requests.exceptions.Timeout:
                    st.error("Operation timed out. The file might be too large or the backend is slow.")
                except Exception as e:
                    st.error(f"Could not reach backend. Make sure FastAPI is running on port 8000.\n\nError: {e}")

# ── Results ───────────────────────────────────────────────────────────────────
if "last_result" in st.session_state:
    result = st.session_state.last_result
    score = result["risk_score"]
    colour = risk_colour(score)
    label = risk_label(score)

    with col_result:
        st.subheader("📊 Risk Assessment")
        st.markdown(
            f"""
            <div style="background:#0d1117; border:2px solid {colour}; border-radius:12px;
                        padding:24px; text-align:center; margin-bottom:12px;">
                <div style="font-size:56px; font-weight:900; color:{colour};">{score}</div>
                <div style="font-size:13px; color:#8b949e; letter-spacing:2px;">THREAT SCORE / 100</div>
                <div style="font-size:20px; margin-top:8px; font-weight:700; color:{colour};">{label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Score bar
        pct = score
        st.markdown(
            f"""
            <div style="background:#21262d; border-radius:6px; height:10px; margin-bottom:18px;">
                <div style="background:{colour}; width:{pct}%; height:10px; border-radius:6px;
                            transition:width 0.5s;"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(f"**Threat Category:** `{result['threat_type']}`")
        st.markdown("---")

        # Findings
        st.subheader("🔎 What Was Found")
        for expl in result["explanation"]:
            st.warning(expl)

        if result["detected_patterns"]:
            with st.expander("🧩 Suspicious Pattern Details"):
                for p in result["detected_patterns"]:
                    st.code(p)

    # ── Full Report & Countermeasures (below) ────────────────────────────
    st.markdown("---")

    tab_report, tab_actions, tab_tips = st.tabs([
        "📄 Full Security Report", "🛡️ Recommended Actions", "💡 Safety Tips"
    ])

    with tab_report:
        st.subheader("📄 Detailed Security Report")
        st.caption("This report is written in plain English so that anyone — technical or not — can understand the findings.")

        full_report = result.get("full_report", "")
        if full_report:
            st.text_area("Report Content", full_report, height=480)

            fname = f"Kavach_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            st.download_button(
                label="⬇️ DOWNLOAD FULL REPORT (TXT)",
                data=full_report,
                file_name=fname,
                mime="text/plain",
                use_container_width=True,
            )
        else:
            st.info("No detailed report available for this scan.")

    with tab_actions:
        st.subheader("🛡️ Recommended Countermeasures")
        st.caption("Follow these steps to protect yourself or your organisation from this threat.")
        recs = result.get("recommendations", [])
        if recs:
            for i, rec in enumerate(recs, 1):
                action = rec["action"] if isinstance(rec, dict) else rec.action
                desc   = rec["description"] if isinstance(rec, dict) else rec.description
                st.markdown(
                    f"""
                    <div style="background:#161b22; border-left:4px solid {colour};
                                border-radius:6px; padding:16px; margin-bottom:12px;">
                        <div style="color:#00ff41; font-weight:700; font-size:15px;">
                            Step {i}. {action}
                        </div>
                        <div style="color:#c9d1d9; font-size:14px; margin-top:6px;">
                            {desc}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.success("✅ No specific actions required. Content appears safe.")

    with tab_tips:
        st.subheader("💡 General Cybersecurity Tips")
        tips = [
            ("🔑", "Never Share OTPs or Passwords",
             "No bank, government agency, or tech company will ever ask for your OTP, PIN, or password over email, SMS, or a phone call."),
            ("🔗", "Think Before You Click",
             "Hover over any link to preview the real destination. If it looks odd or shortened, don't click it — type the website address directly in your browser instead."),
            ("📱", "Enable Two-Factor Authentication (2FA)",
             "2FA adds a second layer of protection. Even if someone steals your password, they can't log in without your phone."),
            ("🔄", "Keep Software Updated",
             "Updates fix security holes that attackers exploit. Enable automatic updates on your phone, computer, and apps."),
            ("🛡️", "Use a Password Manager",
             "Use a strong, unique password for every account. A password manager remembers them all so you don't have to."),
            ("📧", "Verify Unexpected Requests",
             "If you receive an unexpected email or call asking for money or data — even from your 'boss' — verify by calling them directly on a known number."),
            ("🎬", "Be Sceptical of Viral Media",
             "AI can generate fake photos, audio, and videos. If something shocking arrives via WhatsApp or social media, verify it through trusted news sources before sharing."),
            ("🔒", "Use Encrypted Messaging Apps",
             "Apps like Signal or WhatsApp use end-to-end encryption. Avoid sharing sensitive information over unencrypted SMS or email."),
        ]
        for icon, title, body in tips:
            with st.expander(f"{icon}  {title}"):
                st.write(body)

else:
    with col_result:
        st.info("👈 Paste your content on the left and click **RUN SECURITY ANALYSIS** to see the results here.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Kavach AI v2.0 | Real-time Cybersecurity Intelligence Dashboard | Always consult a cybersecurity professional for critical decisions.")
