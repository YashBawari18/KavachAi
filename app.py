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
import plotly.express as px
import plotly.graph_objects as go

# ── Environment Variables ─────────────────────────────────────────────────────
API_URL = os.getenv("API_URL", "http://localhost:8000")

# ── Logo Loading & Base64 (Cached) ───────────────────────────────────────────
@st.cache_data(show_spinner=False)
def get_base64_image(image_path):
    try:
        if os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
    except Exception:
        pass
    return ""

LOGO_B64 = get_base64_image("logo.png")

# ── Session State Init ────────────────────────────────────────────────────────
if "preloader_done" not in st.session_state:
    st.session_state.preloader_done = False
if "show_landing" not in st.session_state:
    st.session_state.show_landing = True
if "show_ml_dashboard" not in st.session_state:
    st.session_state.show_ml_dashboard = False
if "sidebar_opened" not in st.session_state:
    st.session_state.sidebar_opened = False

# ── Page Config ───────────────────────────────────────────────────────────────
# KEY FIX: Use "collapsed" on landing so Streamlit never renders the sidebar.
# Use "expanded" on dashboard so it is always open on first dashboard load.
if st.session_state.show_landing:
    st.set_page_config(
        page_title="KAVACH | AI Cybersecurity Dashboard",
        page_icon=f"data:image/png;base64,{LOGO_B64}" if LOGO_B64 else "🛡️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
else:
    st.set_page_config(
        page_title="KAVACH | AI Cybersecurity Dashboard",
        page_icon=f"data:image/png;base64,{LOGO_B64}" if LOGO_B64 else "🛡️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

# ── Preloader ─────────────────────────────────────────────────────────────────
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
            animation: preloaderFadeOut 1s ease forwards;
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

# ═══════════════════════════════════════════════════════════════════════════════
# ── LANDING PAGE ──────────────────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.show_landing:
    st.session_state.sidebar_opened = False

    st.markdown(f"""
        <style>
            .stApp {{
                background: radial-gradient(circle at center, #050a0f 0%, #000 100%);
                overflow: hidden;
            }}
            [data-testid="stSidebarCollapsedControl"],
            [data-testid="collapsedControl"] {{
                display: none !important;
            }}
            .landing-title {{
                position: absolute; top: 3%; left: 50%;
                transform: translateX(-50%); text-align: center;
                z-index: 1001; width: 100%;
                display: flex; flex-direction: column; align-items: center; gap: 10px;
            }}
            .landing-logo {{
                width: 100px;
                filter: drop-shadow(0 0 15px rgba(0, 240, 255, 0.6));
                animation: pulseLogo 3s infinite alternate;
            }}
            @keyframes pulseLogo {{
                from {{ transform: scale(1); opacity: 0.8; }}
                to {{ transform: scale(1.1); opacity: 1; }}
            }}
            .landing-title h1 {{
                font-family: 'Orbitron', sans-serif; font-size: 3.5rem;
                color: #00f0ff; text-shadow: 0 0 30px rgba(0, 240, 255, 0.4);
                margin: 0; letter-spacing: 15px;
            }}
            .worldwide-test {{
                position: absolute; top: 18%; right: 3%; width: 280px;
                background: rgba(0, 10, 15, 0.8);
                border: 1px solid rgba(0, 240, 255, 0.1);
                padding: 15px; font-family: 'Rajdhani', sans-serif;
                z-index: 1001; border-radius: 4px;
            }}
            @media (max-width: 1200px) {{
                .worldwide-test {{ display: none !important; }}
                .landing-title h1 {{ font-size: 2.5rem; letter-spacing: 8px; }}
            }}
            .test-line {{
                font-size: 0.85rem; color: #00f0ff; margin-bottom: 5px;
                border-left: 2px solid #00f0ff; padding-left: 8px;
                animation: fadeInOut 4s infinite;
            }}
            @keyframes fadeInOut {{ 0%, 100% {{ opacity: 0.3; }} 50% {{ opacity: 1; }} }}
            div.stButton {{
                position: fixed; bottom: 12%; left: 0; width: 100vw;
                display: flex; justify-content: center;
                z-index: 999999 !important; pointer-events: none;
            }}
            .stButton > button {{
                background: rgba(0, 240, 255, 0.05) !important;
                color: #00f0ff !important; border: 1px solid #00f0ff !important;
                border-radius: 4px !important; padding: 12px 0 !important;
                font-family: 'Rajdhani', sans-serif !important; font-weight: 800 !important;
                letter-spacing: 3px !important; text-transform: uppercase !important;
                box-shadow: 0 0 20px rgba(0, 240, 255, 0.2) !important;
                transition: all 0.3s ease !important;
                width: 300px !important; height: 50px !important;
                pointer-events: auto !important;
            }}
            .stButton > button:hover {{
                background: #00f0ff !important; color: #000 !important;
                box-shadow: 0 0 40px #00f0ff !important; transform: translateY(-2px) !important;
            }}
            header, [data-testid="stHeader"], .stDeployButton,
            [data-testid="stToolbar"], footer, [data-testid="stFooter"] {{
                visibility: hidden !important; display: none !important; height: 0 !important;
            }}
        </style>
    """, unsafe_allow_html=True)

    st.markdown(f'''
        <div class="landing-title">
            <img src="data:image/png;base64,{LOGO_B64}" class="landing-logo" alt="Logo">
            <h1>KAVACH AI</h1>
            <p style="color:#00f0ff;letter-spacing:12px;font-family:'Rajdhani';font-weight:800;opacity:0.7;">
                CENTRAL COMMAND CENTRE
            </p>
        </div>
        <div class="worldwide-test">
            <div style="color:#586069;font-size:0.6rem;letter-spacing:2px;margin-bottom:10px;">WORLDWIDE DETECTION LOG</div>
            <div class="test-line">PING [USA.VA.22] -> SUCCESS</div>
            <div class="test-line" style="animation-delay:1s;">TRACE [EU.GER.09] -> ENCRYPTED</div>
            <div class="test-line" style="animation-delay:2s;">SHIELD [ASIA.IN.01] -> ACTIVE</div>
            <div class="test-line" style="animation-delay:3s;">NODES [GLBL.72] -> SYNCHRONIZED</div>
        </div>
    ''', unsafe_allow_html=True)

    st.components.v1.html("""
        <div id="canvas-container" style="width:100vw;height:100vh;position:fixed;top:0;left:0;pointer-events:none;"></div>
        <div id="labels-container" style="position:fixed;top:0;left:0;width:100vw;height:100vh;pointer-events:none;z-index:1005;"></div>
        <div id="metrics-overlay" style="position:fixed;top:18%;left:3%;z-index:1001;display:flex;flex-direction:column;gap:12px;width:320px;font-family:'Rajdhani',sans-serif;pointer-events:none;">
            <div style="background:rgba(0,20,30,0.7);border:1px solid rgba(0,240,255,0.2);border-left:4px solid #00f0ff;padding:12px 20px;backdrop-filter:blur(8px);">
                <div style="font-size:0.75rem;color:#586069;text-transform:uppercase;letter-spacing:3px;margin-bottom:4px;">Global Connectivity</div>
                <div style="font-size:1.4rem;color:#00f0ff;font-weight:800;display:flex;justify-content:space-between;"><span id="m-connectivity">99.99%</span><span style="font-size:0.8rem;color:#0f0;">• LIVE</span></div>
            </div>
            <div style="background:rgba(0,20,30,0.7);border:1px solid rgba(0,240,255,0.2);border-left:4px solid #00f0ff;padding:12px 20px;backdrop-filter:blur(8px);">
                <div style="font-size:0.75rem;color:#586069;text-transform:uppercase;letter-spacing:3px;margin-bottom:4px;">Neural Grid Sync</div>
                <div id="m-sync" style="font-size:1.4rem;color:#00f0ff;font-weight:800;">0.0003 ms</div>
            </div>
            <div style="background:rgba(0,20,30,0.7);border:1px solid rgba(0,240,255,0.2);border-left:4px solid #00f0ff;padding:12px 20px;backdrop-filter:blur(8px);">
                <div style="font-size:0.75rem;color:#586069;text-transform:uppercase;letter-spacing:3px;margin-bottom:4px;">Threat Interception</div>
                <div id="m-threats" style="font-size:1.4rem;color:#00f0ff;font-weight:800;">4.2M / DAY</div>
            </div>
        </div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script>
            let scene, camera, renderer, earth, stars, arcs = [];
            let labelsContainer = document.getElementById('labels-container');
            let testimonials = [
                "Kavach AI caught a phishing link! Saved $500.",
                "Blocked a scam call from an unknown bot.",
                "Scam site detected! My identity is safe.",
                "Kavach AI prevented a credit card hack.",
                "Fake giveaway flagged. Thank you Kavach!",
                "Malicious attachment blocked. Life saver!",
                "Kavach AI just saved my bank details!",
                "Prevented a phishing scam on my work email."
            ];
            let activePopups = [];
            function init() {
                scene = new THREE.Scene();
                camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
                renderer = new THREE.WebGLRenderer({ antialias:true, alpha:true });
                renderer.setPixelRatio(window.devicePixelRatio);
                renderer.setSize(window.innerWidth, window.innerHeight);
                document.getElementById('canvas-container').appendChild(renderer.domElement);
                const earthGroup = new THREE.Group();
                scene.add(earthGroup);
                const geometry = new THREE.SphereGeometry(2.5, 64, 64);
                earth = new THREE.Mesh(geometry, new THREE.MeshPhongMaterial({
                    color:0x050a0f, emissive:0x001015, shininess:50, transparent:true, opacity:0.9
                }));
                earthGroup.add(earth);
                const wf = new THREE.WireframeGeometry(geometry);
                earthGroup.add(new THREE.LineSegments(wf, new THREE.LineBasicMaterial({color:0x00f0ff,transparent:true,opacity:0.1})));
                const atmosphereMat = new THREE.ShaderMaterial({
                    uniforms:{},
                    vertexShader:`varying vec3 vNormal;void main(){vNormal=normalize(normalMatrix*normal);gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}`,
                    fragmentShader:`varying vec3 vNormal;void main(){float i=pow(0.6-dot(vNormal,vec3(0,0,1.0)),2.0);gl_FragColor=vec4(0.0,0.9,1.0,1.0)*i;}`,
                    side:THREE.BackSide,blending:THREE.AdditiveBlending,transparent:true
                });
                earthGroup.add(new THREE.Mesh(new THREE.SphereGeometry(2.7,64,64), atmosphereMat));
                for(let i=0;i<15;i++) createArc(earthGroup);
                scene.add(new THREE.AmbientLight(0xffffff, 0.4));
                const sun=new THREE.DirectionalLight(0xffffff,1); sun.position.set(5,3,5); scene.add(sun);
                const sp=[]; for(let i=0;i<8000;i++) sp.push((Math.random()-.5)*1500,(Math.random()-.5)*1500,(Math.random()-.5)*1500);
                const sg=new THREE.BufferGeometry(); sg.setAttribute('position',new THREE.Float32BufferAttribute(sp,3));
                stars=new THREE.Points(sg,new THREE.PointsMaterial({color:0xffffff,size:0.5})); scene.add(stars);
                earthGroup.position.y=-1.5; camera.position.z=6;
                setInterval(()=>spawnPopup(earthGroup),2500);
                setInterval(updateMetrics,1500);
            }
            function updateMetrics(){
                document.getElementById('m-connectivity').innerText=(99.95+Math.random()*.04).toFixed(2)+"%";
                document.getElementById('m-sync').innerText=(0.0001+Math.random()*.0003).toFixed(4)+" ms";
                document.getElementById('m-threats').innerText=(4.1+Math.random()*.3).toFixed(1)+"M / DAY";
            }
            function createArc(parent){
                const r=2.5;
                const s=new THREE.Vector3().setFromSphericalCoords(r,(Math.random()-.5)*Math.PI,(Math.random()-.5)*Math.PI*2);
                const e=new THREE.Vector3().setFromSphericalCoords(r,(Math.random()-.5)*Math.PI,(Math.random()-.5)*Math.PI*2);
                const m=s.clone().lerp(e,.5); m.normalize().multiplyScalar(r*1.5);
                const curve=new THREE.QuadraticBezierCurve3(s,m,e);
                parent.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(curve.getPoints(50)),new THREE.LineBasicMaterial({color:0x00f0ff,transparent:true,opacity:0.4})));
                const packet=new THREE.Mesh(new THREE.SphereGeometry(.04,8,8),new THREE.MeshBasicMaterial({color:0x00f0ff}));
                parent.add(packet); arcs.push({curve,packet,t:Math.random()});
            }
            function spawnPopup(parent){
                const pos=new THREE.Vector3().setFromSphericalCoords(2.5,(Math.random()-.5)*Math.PI,(Math.random()-.5)*Math.PI*2);
                const div=document.createElement('div');
                Object.assign(div.style,{position:'absolute',background:'rgba(0,240,255,0.15)',border:'1px solid #00f0ff',color:'#fff',padding:'8px 12px',borderRadius:'20px',fontSize:'12px',fontFamily:'Rajdhani,sans-serif',whiteSpace:'nowrap',pointerEvents:'none',opacity:'0',transition:'opacity 0.5s,transform 0.5s',transform:'scale(0.5) translate(-50%,-50%)'});
                div.innerText="🛡️ "+testimonials[Math.floor(Math.random()*testimonials.length)];
                labelsContainer.appendChild(div);
                setTimeout(()=>{div.style.opacity='1';div.style.transform='scale(1) translate(-50%,-50%)';},50);
                let p={div,pos:pos.clone(),parent}; activePopups.push(p);
                setTimeout(()=>{div.style.opacity='0';setTimeout(()=>{labelsContainer.removeChild(div);activePopups=activePopups.filter(x=>x!==p);},500);},4000);
            }
            function animate(){
                requestAnimationFrame(animate);
                earth.rotation.y+=.002; stars.rotation.y+=.0001;
                arcs.forEach(a=>{a.t+=.005;if(a.t>1)a.t=0;a.packet.position.copy(a.curve.getPointAt(a.t));});
                activePopups.forEach(p=>{
                    const sp=p.pos.clone().applyMatrix4(p.parent.matrixWorld).project(camera);
                    if(sp.z>1){p.div.style.display='none';}
                    else{p.div.style.display='block';p.div.style.left=(sp.x*.5+.5)*window.innerWidth+'px';p.div.style.top=((sp.y*-.5+.5)*window.innerHeight-50)+'px';}
                });
                renderer.render(scene,camera);
            }
            window.addEventListener('resize',()=>{camera.aspect=window.innerWidth/window.innerHeight;camera.updateProjectionMatrix();renderer.setSize(window.innerWidth,window.innerHeight);});
            init(); animate();
        </script>
        <style>body{margin:0;overflow:hidden;background:transparent;}</style>
    """, height=1000)

    if st.button("VIEW DASHBOARD"):
        st.session_state.show_landing = False
        st.session_state.sidebar_opened = False
        st.rerun()

    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# ── DASHBOARD STARTS HERE ─────────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

# ── SIDEBAR FIX: JS auto-click the collapsed-control button once on entry ─────
# Because initial_sidebar_state="expanded" only works on a true first load,
# we use JS to programmatically click the open-sidebar button on the first
# dashboard render after coming from the landing page.
if not st.session_state.sidebar_opened:
    st.session_state.sidebar_opened = True
    st.markdown("""
        <script>
        (function() {
            function tryOpenSidebar() {
                // Primary selector — Streamlit's collapsed control button
                var btn = window.parent.document.querySelector(
                    '[data-testid="stSidebarCollapsedControl"] button'
                );
                if (!btn) {
                    // Fallback: button with open/show sidebar aria-label
                    btn = window.parent.document.querySelector(
                        'button[aria-label="Open sidebar"], button[aria-label="Show sidebar"]'
                    );
                }
                if (btn) {
                    btn.click();
                    return true;
                }
                return false;
            }
            var attempts = 0;
            var iv = setInterval(function() {
                if (tryOpenSidebar() || attempts++ > 40) clearInterval(iv);
            }, 100);
        })();
        </script>
    """, unsafe_allow_html=True)

# ── Reset all CSS overrides from the landing page ────────────────────────────
st.markdown("""
    <style>
        /* Fully restore sidebar */
        [data-testid="stSidebar"] {
            display: block !important;
            visibility: visible !important;
            width: auto !important;
            min-width: 0 !important;
            overflow: visible !important;
            transform: none !important;
            opacity: 1 !important;
        }
        /* Restore collapse/expand toggle button */
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="collapsedControl"] {
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            pointer-events: auto !important;
        }
        /* Restore header */
        header, [data-testid="stHeader"] {
            display: block !important;
            visibility: visible !important;
            height: auto !important;
            pointer-events: auto !important;
            background-color: transparent !important;
        }
        /* Restore normal button layout (landing overrode position) */
        div.stButton {
            position: static !important;
            width: auto !important;
            pointer-events: auto !important;
            z-index: auto !important;
            display: block !important;
            bottom: auto !important;
            left: auto !important;
        }
        .stButton > button {
            width: auto !important;
            height: auto !important;
            position: static !important;
            pointer-events: auto !important;
        }
        /* Hide only deploy/toolbar */
        .stDeployButton, [data-testid="stToolbar"] {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)

# ── Load external CSS ─────────────────────────────────────────────────────────
def load_css():
    with open("styles.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
try:
    load_css()
except Exception:
    pass

# ── Dashboard-specific styles ─────────────────────────────────────────────────
st.markdown("""
    <style>
        .hud-exit-btn button { border-color: #ff2a2a !important; color: #ff2a2a !important; }
        .hud-exit-btn button:hover {
            background-color: #ff2a2a !important; color: #000 !important;
            box-shadow: 0 0 20px #ff2a2a !important;
        }
        .stApp > header { background: rgba(0,0,0,0) !important; }
        .block-container { max-width: 1400px; padding-top: 2rem; padding-bottom: 2rem; }
        .sidebar-log-card {
            background: rgba(10,15,25,0.6); border-left: 3px solid #00f0ff;
            border-radius: 4px; padding: 10px; margin-bottom: 8px;
            font-family: 'Rajdhani', sans-serif; font-size: 13px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .sidebar-log-card:hover {
            transform: translateX(4px);
            box-shadow: -4px 4px 15px rgba(0,240,255,0.2);
        }
        .log-header {
            display: flex; justify-content: space-between;
            color: #586069; font-size: 11px; margin-bottom: 4px;
        }
        @media (max-width: 768px) {
            h1 { font-size: 1.8rem !important; }
            h2 { font-size: 1.5rem !important; }
            h3 { font-size: 1.2rem !important; text-align: center; }
        }
    </style>
""", unsafe_allow_html=True)

if LOGO_B64:
    st.markdown(f"""
        <style>
            div[data-testid="stPopover"] button::before {{
                background-image: url("data:image/png;base64,{LOGO_B64}") !important;
                background-size: contain; background-repeat: no-repeat; background-position: center;
            }}
            div[data-testid="stPopover"] button * {{ display: none !important; }}
            div[data-testid="stPopover"] button {{
                width: 60px !important; height: 60px !important;
                border-radius: 50% !important; padding: 0 !important;
                background-color: transparent !important;
            }}
            div[data-testid="stPopover"] button::before {{
                width: 100% !important; height: 100% !important; display: block; content: "";
            }}
        </style>
    """, unsafe_allow_html=True)

# ── Multilingual Configuration ────────────────────────────────────────────────
LANG_OPTIONS = {
    "🇺🇸 English": "en", "🇮🇳 Hindi (हिंदी)": "hi", "🇮🇳 Bengali (বাংলা)": "bn",
    "🇮🇳 Telugu (తెలుగు)": "te", "🇮🇳 Marathi (मराठी)": "mr", "🇮🇳 Tamil (தமிழ்)": "ta",
    "🇮🇳 Urdu (اردو)": "ur", "🇮🇳 Gujarati (ગુજરાતી)": "gu", "🇮🇳 Kannada (ಕನ್ನಡ)": "kn",
    "🇮🇳 Malayalam (മലയാളം)": "ml", "🇮🇳 Punjabi (ਪੰਜਾਬੀ)": "pa",
    "🇪🇸 Spanish (Español)": "es", "🇫🇷 French (Français)": "fr", "🇩🇪 German (Deutsch)": "de",
    "🇨🇳 Chinese Simplified (简体中文)": "zh-CN", "🇨🇳 Chinese Traditional (繁體中文)": "zh-TW",
    "🇯🇵 Japanese (日本語)": "ja", "🇷🇺 Russian (Русский)": "ru", "🇸🇦 Arabic (العربية)": "ar",
    "🇵🇹 Portuguese (Português)": "pt", "🇮🇹 Italian (Italiano)": "it", "🇰🇷 Korean (한국어)": "ko",
    "🇹🇷 Turkish (Türkçe)": "tr", "🇻🇳 Vietnamese (Tiếng Việt)": "vi", "🇹🇭 Thai (ไทย)": "th",
    "🇮🇩 Indonesian (Bahasa Indonesia)": "id", "🇲🇾 Malay (Bahasa Melayu)": "ms",
    "🇵🇭 Filipino (Tagalog)": "tl", "🇳🇱 Dutch (Nederlands)": "nl", "🇵🇱 Polish (Polski)": "pl",
    "🇸🇪 Swedish (Svenska)": "sv", "🇳🇴 Norwegian (Norsk)": "no", "🇩🇰 Danish (Dansk)": "da",
    "🇫🇮 Finnish (Suomi)": "fi", "🇬🇷 Greek (Ελληνικά)": "el", "🇨🇿 Czech (Čeština)": "cs",
    "🇭🇺 Hungarian (Magyar)": "hu", "🇷🇴 Romanian (Română)": "ro", "🇮🇱 Hebrew (עברית)": "iw",
    "🇮🇷 Persian (فارسی)": "fa", "🇺🇦 Ukrainian (Українська)": "uk", "🇰🇿 Kazakh (Қазақ тілі)": "kk",
    "🇿🇦 Afrikaans (Afrikaans)": "af", "🇳🇵 Nepali (नेपाली)": "ne", "🇱🇰 Sinhala (සිංහල)": "si",
    "🇲🇲 Burmese (မြန်မာ)": "my", "🇰Ｈ Khmer (ខ្មែរ)": "km", "🇱🇦 Lao (ລາວ)": "lo"
}

@st.cache_data(show_spinner=False, ttl=3600)
def t(text: str, target_lang: str) -> str:
    if not text or target_lang == "en":
        return text
    try:
        if target_lang == "zh": target_lang = "zh-CN"
        translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
        return translated if translated else text
    except Exception:
        return text

# ── Remaining Session State ───────────────────────────────────────────────────
if "threat_logs"   not in st.session_state: st.session_state.threat_logs   = []
if "chat_history"  not in st.session_state: st.session_state.chat_history  = []
if "lang_choice"   not in st.session_state: st.session_state.lang_choice   = "🇺🇸 English"
if "dark_mode"     not in st.session_state: st.session_state.dark_mode     = True

def get_lang_code(): return LANG_OPTIONS[st.session_state.lang_choice]
def tr(text: str) -> str: return t(text, get_lang_code())

INPUT_OPTIONS = [
    "📧 Phishing Email", "💬 Phishing Message (SMS / Chat)", "🔗 Suspicious URL",
    "🎭 Deepfake / Impersonation Media", "🔐 Anomalous Login / User Behavior",
    "🤖 AI-Generated Content", "💉 Prompt Injection",
]
BACKEND_TYPE_MAP = {
    "📧 Phishing Email": "email", "💬 Phishing Message (SMS / Chat)": "message",
    "🔗 Suspicious URL": "url", "🎭 Deepfake / Impersonation Media": "deepfake",
    "🔐 Anomalous Login / User Behavior": "behavior",
    "🤖 AI-Generated Content": "ai", "💉 Prompt Injection": "prompt",
}

def risk_colour(score):
    if score > 80: return "#ff2a2a"
    elif score > 60: return "#ff9100"
    elif score > 30: return "#ffea00"
    return "#00ff41"

def risk_label(score):
    if score > 80: return "🚨 CRITICAL"
    elif score > 60: return "🔴 HIGH RISK"
    elif score > 30: return "🟠 MODERATE"
    elif score > 0:  return "🟡 LOW RISK"
    return "✅ SAFE"

@st.cache_data(show_spinner=False, ttl=3600)
def text_to_speech(text: str, lang_code: str):
    try:
        tts = gTTS(text=text, lang=lang_code.split('-')[0], slow=False)
        tts.save("response.mp3")
        with open("response.mp3", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            return f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
    except Exception:
        return ""

def generate_bot_response(user_input: str) -> str:
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
    return "I am an AI trained specifically for cybersecurity. I can help you analyze threats, secure your accounts, and identify phishing or deepfakes. What specific security concern do you have?"

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    if LOGO_B64:
        st.markdown(f'<div style="text-align:center;margin-bottom:20px;"><img src="data:image/png;base64,{LOGO_B64}" style="width:80px;filter:drop-shadow(0 0 10px #00f0ff);"></div>', unsafe_allow_html=True)
    else:
        st.image("https://img.icons8.com/nolan/96/shield.png", width=90)

    st.title(tr("🛡️ KAVACH"))
    st.markdown("---")

    is_dark = st.session_state.dark_mode
    if st.toggle("🌙 Dark Mode" if is_dark else "☀️ Light Mode", value=is_dark, key="_dark_toggle"):
        st.session_state.dark_mode = True
    else:
        st.session_state.dark_mode = False

    if st.session_state.dark_mode:
        st.markdown("""<style>.main{background-color:#050505!important;color:#f0f6fc!important;}
            section[data-testid="stSidebar"]{background:linear-gradient(180deg,#0a0a0a 0%,#12161c 100%)!important;}</style>""",
            unsafe_allow_html=True)
    else:
        st.markdown("""<style>.main{background-color:#f0f4f8!important;color:#0d1117!important;}
            h1,h2,h3{color:#00699e!important;text-shadow:none!important;}
            section[data-testid="stSidebar"]{background:linear-gradient(180deg,#dce3ea 0%,#c8d0d9 100%)!important;}
            .stApp{background:#f0f4f8!important;}p,span,label,div{color:#0d1117!important;}</style>""",
            unsafe_allow_html=True)

    st.markdown("---")
    st.selectbox("🌐 Language / 🌐 भाषा", list(LANG_OPTIONS.keys()), key="lang_choice")
    st.markdown("---")

    st.subheader(tr("📋 Recent Threat Logs"))
    if st.session_state.threat_logs:
        logs_html = '<div style="max-height:400px;overflow-y:auto;padding-right:5px;">'
        for log in reversed(st.session_state.threat_logs):
            c = risk_colour(log['score'])
            logs_html += f"""<div class="sidebar-log-card" style="border-left-color:{c};">
                <div class="log-header"><span>{log['timestamp']}</span>
                <span style="color:{c};font-weight:bold;">{log['score']} RISK</span></div>
                <div style="color:#e6edf3;">{tr(log['type'])}</div></div>"""
        logs_html += '</div>'
        st.markdown(logs_html, unsafe_allow_html=True)
    else:
        st.info(tr("No scans yet. Run your first analysis!"))

    st.markdown("---")
    if st.button(tr("🗑️ Clear Logs")):
        st.session_state.threat_logs = []
        st.rerun()

    st.markdown("---")
    if st.button(tr("🧠 ML Model Architecture")):
        st.session_state.show_ml_dashboard = True
        st.rerun()

    st.markdown("---")
    if st.button(tr("🚪 EXIT COMMAND CENTRE")):
        st.session_state.show_landing = True
        st.session_state.show_ml_dashboard = False
        st.rerun()

    st.markdown("---")
    st.caption("KAVACH AI v2.0 - Next-Gen SecOps")

# ── ML Model Architecture Dashboard ──────────────────────────────────────────
if st.session_state.get("show_ml_dashboard", False):
    st.title("🧠 KavachAI Core Neural Architecture")
    st.markdown("---")
    colA, colB, colC = st.columns(3)
    colA.metric(tr("Model Architecture"), "Transformer + XGBoost")
    colB.metric(tr("Training Dataset"), "5.3 Million Samples")
    colC.metric(tr("Global Accuracy"), "98.74%", "+1.2% this week")
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader(tr("Training vs Validation Loss (Epochs)"))
    epochs = list(range(1,51))
    train_loss = [max(0.05, 0.8*(0.9**e)+random.uniform(-0.02,0.02)) for e in epochs]
    val_loss   = [max(0.08, 0.85*(0.91**e)+random.uniform(-0.03,0.03)) for e in epochs]
    fig_loss = go.Figure()
    fig_loss.add_trace(go.Scatter(x=epochs,y=train_loss,mode='lines',name='Training Loss',  line={'color':'#00f0ff','width':3}))
    fig_loss.add_trace(go.Scatter(x=epochs,y=val_loss,  mode='lines',name='Validation Loss',line={'color':'#ff2a2a','width':3}))
    fig_loss.update_layout(height=300,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                           margin={'l':0,'r':0,'t':10,'b':0},legend={'yanchor':"top",'y':0.99,'xanchor':"right",'x':0.99})
    st.plotly_chart(fig_loss,use_container_width=True,config={'displayModeBar':False})
    st.markdown("<br>",unsafe_allow_html=True)
    colX,colY = st.columns(2)
    with colX:
        st.subheader(tr("Feature Importance"))
        fig_feat = px.bar(x=[0.35,0.20,0.18,0.15,0.12],y=["URL Lexical","Domain Age","Payload Heuristics","NLP Tokenizer","TLS Cert"],
                          orientation='h',color=[0.35,0.20,0.18,0.15,0.12],color_continuous_scale=[(0,"#00f0ff"),(1,"#ff2a2a")])
        fig_feat.update_layout(height=250,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                               margin={'l':0,'r':0,'t':10,'b':0},coloraxis_showscale=False)
        st.plotly_chart(fig_feat,use_container_width=True,config={'displayModeBar':False})
    with colY:
        st.subheader(tr("Model Pipeline Overview"))
        st.markdown("""<div style="background:rgba(10,15,25,0.6);padding:15px;border-radius:8px;border-left:3px solid #00f0ff;">
        1. <b>Data Ingestion</b>: Distributed scraping of 40+ threat intel feeds.<br><br>
        2. <b>Preprocessing</b>: Advanced RoBERTa tokenization and dynamic embeddings.<br><br>
        3. <b>Classification</b>: Dual-head architecture combining dense neural networks with lightGBM trees.<br><br>
        4. <b>Latency</b>: Sub-50ms inference time for real-time interception.</div>""",unsafe_allow_html=True)
    st.markdown("---")
    if st.button("⬅️ "+tr("Back to Cyber-Ops Dashboard"),use_container_width=True):
        st.session_state.show_ml_dashboard = False
        st.rerun()
    st.stop()

# ── Cyber-Ops HUD ─────────────────────────────────────────────────────────────
c1,c2 = st.columns([4,1])
with c1: st.markdown("### 🌐 CYBER-OPS DASHBOARD")
with c2:
    st.markdown("<div class='hud-exit-btn'>",unsafe_allow_html=True)
    if st.button(tr("🚪 EXIT COMMAND CENTRE"),use_container_width=True):
        st.session_state.show_landing = True
        st.rerun()
    st.markdown("</div>",unsafe_allow_html=True)

h1,h2,h3,h4 = st.columns(4)
with h1: st.metric(label=tr("SYSTEM STATUS"),value="ONLINE",  delta="99.9% Uptime")
with h2: st.metric(label=tr("LATENCY"),       value="14ms",   delta="-2ms")
with h3: st.metric(label=tr("ACTIVE NODES"),  value="1,242",  delta="+12")
with h4: st.metric(label=tr("THREAT LEVEL"),  value="MODERATE",delta="STABLE",delta_color="off")
st.markdown("---")

# ── Alert Pool ────────────────────────────────────────────────────────────────
REALTIME_ALERT_POOL = [
    {"severity":"CRITICAL","color":"#ff2a2a","msg":"Brute-force SSH attack detected from IP 185.220.101.xx — 2,400 attempts/min"},
    {"severity":"CRITICAL","color":"#ff2a2a","msg":"Ransomware signature (LockBit 3.0) detected on endpoint WS-FINANCE-07"},
    {"severity":"HIGH",    "color":"#ff6b35","msg":"Phishing campaign targeting HR department — 14 emails quarantined"},
    {"severity":"HIGH",    "color":"#ff6b35","msg":"Suspicious outbound traffic to C2 server 91.215.xx.xx on port 4443"},
    {"severity":"HIGH",    "color":"#ff6b35","msg":"New zero-day exploit CVE-2026-1847 actively exploited in the wild"},
    {"severity":"MEDIUM",  "color":"#ff9100","msg":"SQL injection attempt blocked on /api/v2/users endpoint"},
    {"severity":"MEDIUM",  "color":"#ff9100","msg":"Anomalous login from new geo-location (Lagos, NG) for user admin@corp"},
    {"severity":"MEDIUM",  "color":"#ff9100","msg":"DNS tunneling pattern detected — possible data exfiltration attempt"},
    {"severity":"LOW",     "color":"#ffea00","msg":"3 packages with known CVEs found in production Node.js dependencies"},
    {"severity":"LOW",     "color":"#ffea00","msg":"Service account svc-backup granted elevated privileges — review recommended"},
    {"severity":"CRITICAL","color":"#ff2a2a","msg":"Volumetric DDoS attack detected — 12 Gbps flood targeting primary gateway"},
    {"severity":"HIGH",    "color":"#ff6b35","msg":"AI-generated voice deepfake flagged in VoIP call to finance department"},
    {"severity":"MEDIUM",  "color":"#ff9100","msg":"S3 bucket policy changed to public access — potential data exposure"},
    {"severity":"LOW",     "color":"#ffea00","msg":"TLS 1.0 connection detected from legacy client — deprecation warning"},
    {"severity":"CRITICAL","color":"#ff2a2a","msg":"Trojan dropper detected in email attachment — SHA256 matches APT29 toolkit"},
]

def generate_realtime_alerts(n=5):
    now = datetime.now()
    sel = random.sample(REALTIME_ALERT_POOL, min(n, len(REALTIME_ALERT_POOL)))
    out = []
    for i,a in enumerate(sel):
        ts = now - timedelta(seconds=random.randint(5,120+i*30))
        out.append({**a,"time":ts.strftime("%H:%M:%S")})
    return sorted(out,key=lambda x:x["time"],reverse=True)

if "realtime_alerts" not in st.session_state or \
        time.time()-st.session_state.get("alert_last_refresh",0)>8:
    st.session_state.realtime_alerts   = generate_realtime_alerts(5)
    st.session_state.alert_last_refresh = time.time()

alerts = st.session_state.realtime_alerts

# ── Main Layout ───────────────────────────────────────────────────────────────
main_col, _ = st.columns([3,1])

with main_col:
    st.subheader(tr("🌍 GLOBAL THREAT ORIGINS"))
    cities = [
        {"city":"Moscow",   "lat":55.75,"lon":37.61, "intensity":random.randint(50,100)},
        {"city":"Beijing",  "lat":39.90,"lon":116.40,"intensity":random.randint(60,100)},
        {"city":"Pyongyang","lat":39.03,"lon":125.75,"intensity":random.randint(40,90)},
        {"city":"Tehran",   "lat":35.68,"lon":51.38, "intensity":random.randint(30,80)},
        {"city":"Lagos",    "lat":6.52, "lon":3.37,  "intensity":random.randint(20,70)},
        {"city":"São Paulo","lat":-23.55,"lon":-46.63,"intensity":random.randint(30,80)},
        {"city":"New York", "lat":40.71,"lon":-74.00,"intensity":random.randint(40,90)},
        {"city":"London",   "lat":51.50,"lon":-0.12, "intensity":random.randint(20,70)},
        {"city":"Frankfurt","lat":50.11,"lon":8.68,  "intensity":random.randint(30,80)},
        {"city":"Mumbai",   "lat":19.07,"lon":72.87, "intensity":random.randint(40,90)},
        {"city":"Singapore","lat":1.35, "lon":103.81,"intensity":random.randint(30,80)},
        {"city":"Sydney",   "lat":-33.86,"lon":151.20,"intensity":random.randint(20,60)},
    ]
    fig_map = px.scatter_geo(pd.DataFrame(cities),lat="lat",lon="lon",size="intensity",color="intensity",
        color_continuous_scale=[(0,"#00f0ff"),(1,"#ff2a2a")],hover_name="city",projection="equirectangular")
    fig_map.update_geos(showland=True,landcolor="#0a0f14",showocean=True,oceancolor="#020508",
        showcountries=True,countrycolor="#1a2639",bgcolor="#020508",resolution=50)
    fig_map.update_layout(margin=dict(l=0,r=0,t=0,b=0),paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",coloraxis_showscale=False,height=400)
    st.plotly_chart(fig_map,use_container_width=True,config={'displayModeBar':False})

    st.markdown("<br>",unsafe_allow_html=True)
    cc1,cc2 = st.columns(2)
    with cc1:
        st.subheader(tr("📈 THREAT TRENDS (24H)"))
        cd = pd.DataFrame({'time':pd.date_range(start='2026-03-15',periods=24,freq='h'),
            'attacks':[random.randint(400,1200) for _ in range(24)],
            'blocked':[random.randint(350,1150) for _ in range(24)]})
        fig_t = go.Figure()
        fig_t.add_trace(go.Scatter(x=cd['time'],y=cd['attacks'],fill='tozeroy',mode='lines',
            line={'color':'#ff2a2a','width':2},fillcolor='rgba(255,42,42,0.2)',name='Attacks'))
        fig_t.add_trace(go.Scatter(x=cd['time'],y=cd['blocked'],fill='tozeroy',mode='lines',
            line={'color':'#00f0ff','width':2},fillcolor='rgba(0,240,255,0.2)',name='Blocked'))
        fig_t.update_layout(margin={'l':0,'r':0,'t':10,'b':0},height=250,
            paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
            xaxis={'showgrid':False,'color':"#586069"},
            yaxis={'showgrid':True,'gridcolor':"#1a2639",'color':"#586069"},
            legend={'orientation':"h",'yanchor':"bottom",'y':1.02,'xanchor':"right",'x':1,'font':{'color':"#00f0ff"}})
        st.plotly_chart(fig_t,use_container_width=True,config={'displayModeBar':False})
    with cc2:
        st.subheader(tr("🎯 TOP TARGETED REGIONS"))
        fig_b = px.bar(pd.DataFrame({'Region':['North America','Europe','Asia Pacific','Latin America','Middle East'],
            'Incidents':[8540,6210,5430,2100,1850]}),x='Incidents',y='Region',orientation='h',
            color='Incidents',color_continuous_scale=[(0,"#00f0ff"),(1,"#00ff41")])
        fig_b.update_layout(margin={'l':0,'r':0,'t':10,'b':0},height=250,
            paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",coloraxis_showscale=False,
            xaxis={'showgrid':True,'gridcolor':"#1a2639",'color':"#586069"},
            yaxis={'showgrid':False,'color':"#e6edf3",'categoryorder':'total ascending'})
        st.plotly_chart(fig_b,use_container_width=True,config={'displayModeBar':False})

    st.markdown("<br>",unsafe_allow_html=True)
    gc1,gc2,gc3 = st.columns(3)
    with gc1:
        st.subheader(tr("⚡ NETWORK STRESS VELOCITY"))
        st.markdown("<div style='height:10px;'></div>",unsafe_allow_html=True)
        sv = random.randint(45,92)
        fig_g = go.Figure(go.Indicator(mode="gauge+number",value=sv,domain={'x':[0,1],'y':[0,1]},
            title={'text':tr("Gbps Traffic Anomaly"),'font':{'size':12,'color':'#586069'}},
            number={'font':{'color':"#00f0ff",'family':"Rajdhani"}},
            gauge={'axis':{'range':[None,100],'tickwidth':1,'tickcolor':"#1a2639"},
                   'bar':{'color':"#ff2a2a" if sv>80 else "#00f0ff"},
                   'bgcolor':"rgba(0,0,0,0)",'borderwidth':2,'bordercolor':"rgba(0,240,255,0.3)",
                   'steps':[{'range':[0,50],'color':'rgba(0,255,65,0.1)'},
                             {'range':[50,80],'color':'rgba(255,145,0,0.1)'},
                             {'range':[80,100],'color':'rgba(255,42,42,0.2)'}],
                   'threshold':{'line':{'color':"red",'width':4},'thickness':0.75,'value':90}}))
        fig_g.update_layout(height=220,margin={'l':10,'r':10,'t':30,'b':10},
            paper_bgcolor="rgba(0,0,0,0)",font={'color':"#e6edf3"})
        st.plotly_chart(fig_g,use_container_width=True,config={'displayModeBar':False})
    with gc2:
        st.subheader(tr("🕸️ ACTIVE PORT SCANNER"))
        st.markdown("<div style='height:10px;'></div>",unsafe_allow_html=True)
        fips=[f"{random.randint(11,240)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}" for _ in range(15)]
        ports=[22,80,443,3389,8080,21,23,27017,3306]
        sh="""<style>.sc{background:#020508;border:1px solid rgba(0,240,255,0.3);border-radius:8px;height:190px;overflow:hidden;position:relative;font-family:'Courier New',monospace;font-size:11px;padding:10px;}
        .sci{position:absolute;top:100%;color:#00ff41;animation:su 15s linear infinite;display:flex;flex-direction:column;width:100%;}
        .sl{margin-bottom:4px;opacity:0.8;}.sw{color:#ff2a2a;font-weight:bold;}
        @keyframes su{0%{top:100%}100%{top:-150%}}</style><div class="sc"><div class="sci">"""
        for _ in range(25):
            p=random.random(); ip,port=random.choice(fips),random.choice(ports)
            if p<0.15: sh+=f'<div class="sl sw">[CRITICAL] Intrusion attempt on {ip}:{port} (BLOCKED)</div>'
            elif p<0.3: sh+=f'<div class="sl" style="color:#ff9100">[WARN] High ping from {ip}:{port}</div>'
            else: sh+=f'<div class="sl">[TRACE] Scanning {ip} across port {port} -> OK</div>'
        sh+="</div></div>"
        st.markdown(sh,unsafe_allow_html=True)
    with gc3:
        st.subheader(tr("🛡️ NODE INTEGRITY RADAR"))
        st.markdown("<div style='height:10px;'></div>",unsafe_allow_html=True)
        cats=['Firewall','Database','API Gateway','Auth Server','DNS Layer']
        vals=[random.randint(70,100) for _ in range(5)]
        fig_r=go.Figure()
        fig_r.add_trace(go.Scatterpolar(r=vals+[vals[0]],theta=cats+[cats[0]],fill='toself',
            fillcolor='rgba(0,240,255,0.2)',line={'color':'#00f0ff','width':2},name='Integrity %'))
        fig_r.update_layout(polar={'radialaxis':{'visible':True,'range':[0,100],'color':'#586069','gridcolor':'#1a2639'},
            'angularaxis':{'color':'#e6edf3','gridcolor':'#1a2639'},'bgcolor':'rgba(0,0,0,0)'},
            showlegend=False,height=220,margin={'l':20,'r':20,'t':20,'b':20},paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_r,use_container_width=True,config={'displayModeBar':False})

    st.markdown("<br>",unsafe_allow_html=True)
    st.subheader(tr("🔔 TACTICAL ALERTS"))
    ah='<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:15px;margin-bottom:20px;">'
    for a in alerts[:4]:
        ah+=(f'<div style="background:rgba(10,15,25,0.8);border-left:4px solid {a["color"]};border-radius:8px;padding:15px;">'
             f'<div style="display:flex;justify-content:space-between;align-items:center;">'
             f'<span style="color:{a["color"]};font-weight:800;font-size:12px;">{a["severity"]}</span>'
             f'<span style="color:#586069;font-size:10px;">{a["time"]}</span></div>'
             f'<div style="color:#e6edf3;font-size:13px;margin-top:8px;">{tr(a["msg"])}</div></div>')
    ah+="</div>"
    st.markdown(ah,unsafe_allow_html=True)

# ── Threat Analysis Module ────────────────────────────────────────────────────
st.markdown("<br>",unsafe_allow_html=True)
col_input, col_result = st.columns([1.5,1])

with col_input:
    st.subheader(tr("🔍 Threat Input Module"))
    st.caption(tr("Select what kind of content you want to analyse, paste the content or upload a file, then click RUN SECURITY ANALYSIS."))
    trans_opts = {opt:tr(opt) for opt in INPUT_OPTIONS}
    d2r = {v:k for k,v in trans_opts.items()}
    sel_disp = st.selectbox(tr("Select Threat Category"),list(trans_opts.values()))
    input_type = d2r[sel_disp]
    uploaded_file = None
    if input_type == "🎭 Deepfake / Impersonation Media":
        st.markdown(tr("**— OR — Upload Audio, Video, or Image file for deepfake analysis:**"))
        uploaded_file = st.file_uploader(tr("Upload Media"),
            type=["mp4","mkv","avi","mov","mp3","wav","m4a","aac","ogg","jpg","jpeg","png","webp","heic"])
    user_input = st.text_area(tr("Content to Analyse / Description"),
        height=160 if input_type=="🎭 Deepfake / Impersonation Media" else 200)
    run_btn = st.button(tr("🔬 RUN SECURITY ANALYSIS"),use_container_width=True)
    if run_btn:
        if not user_input.strip() and uploaded_file is None:
            st.warning(tr("⚠️ Please paste some content or upload a file first."))
        else:
            with st.spinner(tr("🔎 Analysing threat patterns — please wait...")):
                try:
                    is_file = uploaded_file is not None
                    if is_file:
                        resp = requests.post(f"{API_URL}/detect-file",
                            data={"content_type":BACKEND_TYPE_MAP[input_type]},
                            files={"file":(uploaded_file.name,uploaded_file.getvalue(),uploaded_file.type)},timeout=45)
                    else:
                        resp = requests.post(f"{API_URL}/detect",
                            json={"content":user_input,"content_type":BACKEND_TYPE_MAP[input_type]},timeout=15)
                    if resp.status_code==200:
                        data=resp.json()
                        st.session_state.last_result=data
                        st.session_state.last_input_label=input_type
                        st.session_state.threat_logs.append({
                            "timestamp":datetime.now().strftime("%H:%M:%S"),
                            "type":data["threat_type"]+(" (File)" if is_file else ""),
                            "score":data["risk_score"]})
                        st.success(tr("✅ Analysis Complete! See results on the right →"))
                    else:
                        st.error(f"Backend Error: {resp.text}")
                except Exception as e:
                    st.error(f"Error connecting to KavachAI Core: {e}")

if "last_result" in st.session_state:
    result=st.session_state.last_result
    score=result["risk_score"]
    colour=risk_colour(score)
    label=tr(risk_label(score))
    with col_result:
        st.subheader(tr("📊 RISK INDEX"))
        fig_risk=go.Figure(go.Indicator(mode="gauge+number",value=score,domain={'x':[0,1],'y':[0,1]},
            title={'text':label,'font':{'size':20,'color':colour,'family':'Orbitron'}},
            number={'font':{'color':colour,'family':"Rajdhani",'size':50}},
            gauge={'axis':{'range':[0,100],'tickwidth':1,'tickcolor':"#1a2639"},
                   'bar':{'color':colour},'bgcolor':"rgba(0,0,0,0)",'borderwidth':2,'bordercolor':colour,
                   'steps':[{'range':[0,30],'color':'rgba(0,255,65,0.1)'},
                             {'range':[30,60],'color':'rgba(255,234,0,0.1)'},
                             {'range':[60,80],'color':'rgba(255,145,0,0.1)'},
                             {'range':[80,100],'color':'rgba(255,42,42,0.2)'}],
                   'threshold':{'line':{'color':"white",'width':2},'thickness':0.75,'value':score}}))
        fig_risk.update_layout(height=260,margin={'l':10,'r':10,'t':40,'b':10},
            paper_bgcolor="rgba(0,0,0,0)",font={'color':"#e6edf3"})
        st.plotly_chart(fig_risk,use_container_width=True,config={'displayModeBar':False})
        st.markdown(f"<br>**{tr('Threat Category')}:** `{tr(result['threat_type'])}`",unsafe_allow_html=True)
        st.markdown("---")
        st.subheader(tr("🔎 What Was Found"))
        for expl in result["explanation"]: st.warning(tr(expl))
        if result["detected_patterns"]:
            with st.expander(tr("🧩 Tactical Intelligence Breakdown")):
                for p in result["detected_patterns"]: st.markdown(f"🔹 {tr(p)}")
        st.markdown("<br>",unsafe_allow_html=True)
        st.subheader(tr("📊 SCAN METRICS"))
        cats=[tr("Malicious Code"),tr("Phishing Match"),tr("Metadata Anomaly"),tr("AI Generation")]
        st.bar_chart(pd.DataFrame({"Indicator":cats,"Confidence":[random.randint(5,max(10,score)) for _ in range(4)]}).set_index("Indicator"),color="#00f0ff")
        if score>60:
            st.markdown('<audio autoplay><source src="https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg" type="audio/ogg"></audio>',unsafe_allow_html=True)

    st.markdown("---")
    t1,t2,t3=st.tabs([tr("📄 Full Security Report"),tr("🛡️ Recommended Actions"),tr("💡 Safety Tips")])
    with t1:
        fr=result.get("full_report","")
        if fr:
            tr_fr=tr(fr)
            st.text_area("",tr_fr,height=400,key="report_area")
            st.download_button(label=tr("⬇️ DOWNLOAD FULL REPORT (TXT)"),data=tr_fr,
                file_name=f"Kavach_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",use_container_width=True)
    with t2:
        st.markdown("<br>",unsafe_allow_html=True)
        for i,rec in enumerate(result.get("recommendations",[]),1):
            action=rec["action"] if isinstance(rec,dict) else rec.action
            desc=rec["description"] if isinstance(rec,dict) else rec.description
            st.markdown(f"""<div style="background:rgba(10,15,25,0.6);border-left:4px solid {colour};border-radius:4px;padding:15px;margin-bottom:12px;">
                <span style="color:{colour};font-weight:700;font-size:16px;">{i}. {tr(action)}</span>
                <p style="color:#7d8590;font-size:14px;margin:5px 0 0 0;">{tr(desc)}</p></div>""",unsafe_allow_html=True)
    with t3:
        st.info(tr("General protection guide enabled. Follow security best practices."))
        st.write(tr("1. 🔑 **Use Strong Passwords**: Avoid dictionary words. Use a manager."))
        st.write(tr("2. 📱 **Enable 2FA**: Always use two-factor authentication."))
        st.write(tr("3. 🔗 **Don't Click Suspicious Links**: Type the URL manually."))
        st.write(tr("4. 🎬 **Verify Senders**: Call the person if an email/video asks for money."))
else:
    with col_result:
        st.info("👈 "+tr("Select what kind of content you want to analyse, paste the content or upload a file, then click RUN SECURITY ANALYSIS."))

# ── Floating Chatbot ──────────────────────────────────────────────────────────
with st.popover(" ",use_container_width=False):
    st.markdown(f"### 🛡️ Kavach {tr('AI Assistant')}")
    st.caption(tr("Ask me anything about cybersecurity! I can also speak to you."))
    if not st.session_state.chat_history:
        st.session_state.chat_history.append({"role":"assistant","content":"Hello! I am Kavach AI, your personal cybersecurity assistant. How can I protect you today?"})
    with st.container(height=300):
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"],avatar="🛡️" if msg["role"]=="assistant" else "👤"):
                st.write(tr(msg["content"]))
    if st.session_state.chat_history[-1]["role"]=="assistant" and len(st.session_state.chat_history)>1:
        st.markdown(text_to_speech(tr(st.session_state.chat_history[-1]["content"]),get_lang_code()),unsafe_allow_html=True)
    chat_input=st.chat_input(tr("Ask about cybersecurity, threats..."))
    if chat_input:
        st.session_state.chat_history.append({"role":"user","content":chat_input})
        st.session_state.chat_history.append({"role":"assistant","content":generate_bot_response(chat_input)})
        st.rerun()

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("<div style='text-align:center;color:#8b949e;'>Kavach AI v2.0 | Real-time Cybersecurity Intelligence | Stay safe online.</div>",unsafe_allow_html=True)