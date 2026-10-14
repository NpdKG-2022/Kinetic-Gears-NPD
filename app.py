import base64
import io
import os
import random
import time
import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Kinetic Gears - Drawing Viewer",
    page_icon="KG-Logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Helper function to convert logo to base64
@st.cache_data
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return ""

logo_base64 = get_base64_image("KG-Logo.png")

# List of random mechanical manufacturing & engineering wallpapers
manufacturing_wallpapers = [
    "https://images.unsplash.com/photo-1565043589221-1a6fd9ae45c7?q=80&w=1920&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?q=80&w=1920&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1581092160607-ee22621dd758?q=80&w=1920&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1504917595217-d4dc5ebe6122?q=80&w=1920&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1537462715879-360eeb61a0ad?q=80&w=1920&auto=format&fit=crop",
]

selected_wallpaper = random.choice(manufacturing_wallpapers)

# Custom CSS for Glassmorphism login, layouts, and containers
st.markdown(
    f"""
    <style>
        /* Full page background with dynamic mechanical wallpaper */
        .stApp {{
            background: linear-gradient(rgba(15, 12, 29, 0.65), rgba(15, 12, 29, 0.85)),
                        url('{selected_wallpaper}');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        /* --- GLASSMORPHISM LOGIN FORM STYLING --- */
        div[data-testid="stForm"] {{
            background: rgba(255, 255, 255, 0.08) !important;
            backdrop-filter: blur(16px) saturate(180%) !important;
            -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 24px !important;
            padding: 40px 30px !important;
            box-shadow: 0 30px 60px rgba(0, 0, 0, 0.4) !important;
        }}

        div[data-testid="stTextInput"] input {{
            background-color: transparent !important;
            border: none !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.5) !important;
            border-radius: 0px !important;
            color: #ffffff !important;
            padding: 10px 5px !important;
            font-size: 15px !important;
        }}
        div[data-testid="stTextInput"] input:focus {{
            border-bottom: 2px solid #ffffff !important;
            box-shadow: none !important;
        }}
        div[data-testid="stTextInput"] label {{
            color: rgba(255, 255, 255, 0.9) !important;
            font-weight: 500 !important;
        }}

        div[data-testid="stFormSubmitButton"] button {{
            background-color: #ffffff !important;
            color: #111111 !important;
            font-weight: 700 !important;
            border-radius: 30px !important;
            border: none !important;
            height: 48px !important;
            font-size: 16px !important;
            margin-top: 15px !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
            transition: all 0.3s ease !important;
        }}
        div[data-testid="stFormSubmitButton"] button:hover {{
            background-color: #f0f0f0 !important;
            transform: translateY(-2px);
        }}

        /* Make dataframes take full width and wrap cleanly */
        [data-testid="stDataFrame"] {{
            width: 100% !important;
        }}
        [data-testid="stDataFrame"] > div {{
            width: 100% !important;
        }}
    </style>
""",
    unsafe_allow_html=True,
)

# ================= USER AUTHENTICATION & PERSISTENCE SETUP =================
USERS = {
    "admin": {"password": "admin123", "role": "Admin"},
}

SESSION_TIMEOUT = 600  # 10 minutes in seconds

query_params = st.query_params

if "logged_in" not in st.session_state:
    qp_logged_in = query_params.get("logged_in") == "True"
    qp_username = query_params.get("username", "")
    qp_login_time = float(query_params.get("login_time", 0.0))

    if qp_logged_in and qp_username in USERS:
        elapsed = time.time() - qp_login_time
        if elapsed < SESSION_TIMEOUT:
            st.session_state["logged_in"] = True
            st.session_state["username"] = qp_username
            st.session_state["role"] = USERS[qp_username]["role"]
            st.session_state["login_time"] = qp_login_time
        else:
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            st.session_state["role"] = ""
            st.session_state["login_time"] = 0.0
            st.query_params.clear()
    else:
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.session_state["role"] = ""
        st.session_state["login_time"] = 0.0


def login_screen():
    st.markdown("<br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1.2, 1])

    with col2:
        with st.form("login_form"):
            if logo_base64:
                st.markdown(
                    f"""
                    <div style="text-align: center; margin-bottom: 5px;">
                        <img src="data:image/png;base64,{logo_base64}" width="70" style="display: block; margin: 0 auto;" />
                    </div>
                """,
                    unsafe_allow_html=True,
                )

            st.markdown(
                "<h1 style='text-align: center; color: white; font-weight: 700; margin-bottom: 25px;'>Login</h1>",
                unsafe_allow_html=True,
            )

            username_input = st.text_input("Email", placeholder="Enter username or email")
            password_input = st.text_input("Password", type="password", placeholder="Enter password")
            
            st.markdown(
                """
                <div style="display: flex; justify-content: space-between; align-items: center; font-size: 13px; margin: 10px 0 15px 0;">
                    <span style="color: rgba(255,255,255,0.8);"><input type="checkbox" style="margin-right: 5px;"> Remember me</span>
                    <a href="#" style="color: #ffffff; text-decoration: none;">Forget Password</a>
                </div>
                """,
                unsafe_allow_html=True,
            )

            submit_button = st.form_submit_button("Log in", use_container_width=True)

            if submit_button:
                if (
                    username_input in USERS
                    and USERS[username_input]["password"] == password_input
                ):
                    current_time = time.time()
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = username_input
                    st.session_state["role"] = USERS[username_input]["role"]
                    st.session_state["login_time"] = current_time

                    st.query_params["logged_in"] = "True"
                    st.query_params["username"] = username_input
                    st.query_params["login_time"] = str(current_time)

                    st.success(f"Welcome back, {username_input}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password. Please try again.")

        st.markdown(
            """
            <div style="text-align: center; margin-top: 20px; color: rgba(255,255,255,0.8); font-size: 14px;">
                Don't have an account? <a href="#" style="color: white; font-weight: 600; text-decoration: none;">Register</a>
            </div>
            """,
            unsafe_allow_html=True,
        )


if not st.session_state["logged_in"]:
    login_screen()
    st.stop()

# ================= PROFESSIONAL SIDEBAR WITH LOGO =================
with st.sidebar:
    if logo_base64:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 10px 0 20px 0;">
                <img src="data:image/png;base64,{logo_base64}" width="65" style="display: block; margin: 0 auto 10px auto;" />
                <h3 style="margin: 0; font-size: 18px; color: #ffffff; letter-spacing: 1px;">KINETIC GEARS</h3>
                <p style="margin: 2px 0 0 0; font-size: 11px; color: rgba(255,255,255,0.6);">Drawing Management System</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("---")
    st.markdown("<p style='font-size: 12px; color: rgba(255,255,255,0.7); text-align: center;'>System operational & secure.</p>", unsafe_allow_html=True)

# Handle logout trigger via query param
if st.query_params.get("do_logout") == "true":
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.session_state["role"] = ""
    st.session_state["login_time"] = 0.0
    st.query_params.clear()
    st.rerun()

# ================= TOP HEADER BAR =================
top_c1, top_c2, top_c3, top_c4 = st.columns([1.2, 2.3, 1.1, 0.9])

with top_c1:
    st.markdown(
        f"<div style='color: white;'>👤 <b>{st.session_state['username']}</b><br>Role:"
        f" <b>{st.session_state['role']}</b></div>",
        unsafe_allow_html=True,
    )

with top_c2:
    st.components.v1.html(
        """
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&display=swap" rel="stylesheet">
        <style>
            body { margin: 0; background-color: transparent; }
            .clock-card {
                background: linear-gradient(135deg, #e91e63, #c2185b);
                border-radius: 14px;
                padding: 6px 14px;
                text-align: center;
                box-shadow: 0 4px 15px rgba(233, 30, 99, 0.3);
                font-family: 'Orbitron', sans-serif;
                display: inline-block;
                box-sizing: border-box;
            }
            .time-display {
                font-size: 18px;
                font-weight: 700;
                color: #ffffff;
                letter-spacing: 2px;
                text-shadow: 0 0 10px rgba(255, 255, 255, 0.6);
            }
            .date-display {
                font-size: 10px;
                font-weight: 500;
                color: #fce4ec;
                margin-top: 2px;
                letter-spacing: 1px;
            }
        </style>
        <div class="clock-card">
            <div id="futuristic-time" class="time-display">00:00:00 AM</div>
            <div id="futuristic-date" class="date-display">Loading date...</div>
        </div>
        <script>
            function updateFuturisticClock() {
                const now = new Date();
                let hours = now.getHours();
                const minutes = String(now.getMinutes()).padStart(2, '0');
                const seconds = String(now.getSeconds()).padStart(2, '0');
                const ampm = hours >= 12 ? 'PM' : 'AM';
                hours = hours % 12;
                hours = hours ? hours : 12; 
                const formattedHours = String(hours).padStart(2, '0');
                document.getElementById('futuristic-time').innerText = formattedHours + ":" + minutes + ":" + seconds + " " + ampm;
                const options = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' };
                document.getElementById('futuristic-date').innerText = now.toLocaleDateString('en-US', options);
            }
            setInterval(updateFuturisticClock, 1000);
            updateFuturisticClock();
        </script>
        """,
        height=55,
    )

with top_c3:
    st.components.v1.html(
        f"""
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&display=swap" rel="stylesheet">
        <style>
            body {{ margin: 0; background-color: transparent; }}
            .expire-card {{
                font-family: 'Orbitron', sans-serif;
                color: #ffffff;
                font-size: 12px;
            }}
            .expire-timer {{
                font-size: 14px;
                font-weight: 700;
                color: #ff4081;
                letter-spacing: 1px;
            }}
        </style>
        <div class="expire-card">
            ⏳ Expires:<br>
            <div id="countdown-timer" class="expire-timer">10:00</div>
        </div>
        <script>
            const timeoutDuration = {SESSION_TIMEOUT} * 1000;
            let lastActivity = Date.now();
            function resetTimer() {{ lastActivity = Date.now(); }}
            window.addEventListener('mousemove', resetTimer, {{ passive: true }});
            window.addEventListener('mousedown', resetTimer, {{ passive: true }});
            window.addEventListener('click', resetTimer, {{ passive: true }});
            window.addEventListener('keypress', resetTimer, {{ passive: true }});
            window.addEventListener('scroll', resetTimer, {{ passive: true }});
            window.addEventListener('touchstart', resetTimer, {{ passive: true }});

            function updateExpiryCountdown() {{
                const now = Date.now();
                const elapsed = now - lastActivity;
                const remaining = timeoutDuration - elapsed;
                if (remaining <= 0) {{
                    document.getElementById('countdown-timer').innerText = "00:00";
                    window.location.href = "?do_logout=true";
                    return;
                }}
                const totalSecs = Math.floor(remaining / 1000);
                const mins = String(Math.floor(totalSecs / 60)).padStart(2, '0');
                const secs = String(totalSecs % 60).padStart(2, '0');
                document.getElementById('countdown-timer').innerText = mins + ":" + secs;
            }
            setInterval(updateExpiryCountdown, 1000);
            updateExpiryCountdown();
        </script>
        """,
        height=50,
    )

with top_c4:
    st.markdown("<br>", unsafe_allow_html=True)
    st.components.v1.html(
        """
        <style>
            body { margin: 0; background: transparent; display: flex; justify-content: flex-end; }
            .logout-container { display: flex; align-items: center; justify-content: flex-end; }
            .logout-btn {
                display: flex; align-items: center; background-color: #f44336; color: white;
                text-decoration: none; border-radius: 30px; width: 42px; height: 42px;
                overflow: hidden; box-shadow: 0 4px 15px rgba(244, 67, 54, 0.4);
                transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.3s ease;
                cursor: pointer; white-space: nowrap;
            }
            .logout-btn:hover { width: 135px; background-color: #d32f2f; }
            .logout-icon { min-width: 42px; height: 42px; display: flex; align-items: center; justify-content: center; }
            .logout-icon svg { width: 22px; height: 22px; fill: none; stroke: white; stroke-width: 2.5; stroke-linecap: round; stroke-linejoin: round; }
            .logout-text { font-family: sans-serif; font-weight: 600; font-size: 14px; padding-left: 2px; padding-right: 15px; opacity: 0; transition: opacity 0.3s ease 0.1s; }
            .logout-btn:hover .logout-text { opacity: 1; }
        </style>
        <div class="logout-container">
            <a href="?do_logout=true" target="_self" class="logout-btn" title="Logout">
                <div class="logout-icon">
                    <svg viewBox="0 0 24 24">
                        <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                        <polyline points="16 17 21 12 16 7"></polyline>
                        <line x1="21" y1="12" x2="9" y2="12"></line>
                    </svg>
                </div>
                <div class="logout-text">Logout</div>
            </a>
        </div>
        """,
        height=50,
    )

st.markdown("---")

# ================= DRAWING VIEWER INTERFACE =================
st.subheader("📐 Technical Drawing Viewer")

drawings_df = None
if os.path.exists("item_drawings.csv"):
    try:
        drawings_df = pd.read_csv("item_drawings.csv")
    except Exception:
        pass

col_d1, col_d2 = st.columns([1, 2])

with col_d1:
    st.markdown("#### Select Item / Drawing")
    drawing_files = []
    if os.path.exists("drawings") and os.path.isdir("drawings"):
        drawing_files = [f for f in os.listdir("drawings") if f.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf', '.webp'))]
    
    if drawings_df is not None and not drawings_df.empty:
        st.dataframe(drawings_df, use_container_width=True)
        item_options = drawings_df.iloc[:, 0].astype(str).tolist()
        selected_item = st.selectbox("Choose Item Code / Name:", item_options)
        
        matched_row = drawings_df[drawings_df.iloc[:, 0].astype(str) == selected_item]
        target_file = None
        if not matched_row.empty:
            for col in matched_row.columns:
                val = str(matched_row[col].values[0])
                if any(val.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.pdf', '.webp']):
                    target_file = val
                    break
        if not target_file and drawing_files:
            target_file = drawing_files[0]
    else:
        if drawing_files:
            selected_item = st.selectbox("Available Drawing Files:", drawing_files)
            target_file = selected_item
        else:
            target_file = None
            st.warning("No drawings found in `drawings/` folder or `item_drawings.csv`.")

with col_d2:
    st.markdown("#### Drawing Preview & Specifications")
    if target_file:
        file_path = os.path.join("drawings", target_file) if not os.path.exists(target_file) else target_file
        if os.path.exists(file_path):
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                st.image(file_path, caption=f"Drawing: {target_file}", use_column_width=True)
            elif file_path.lower().endswith('.pdf'):
                st.success(f"PDF Drawing loaded: {target_file}")
                with open(file_path, "rb") as pdf_file:
                    PDFbyte = pdf_file.read()
                st.download_button(label="📥 Download Drawing PDF", data=PDFbyte, file_name=target_file, mime='application/pdf')
        else:
            st.error(f"Drawing file '{target_file}' could not be located in the drawings folder.")
    else:
        st.info("Select an item to view its technical drawing.")
