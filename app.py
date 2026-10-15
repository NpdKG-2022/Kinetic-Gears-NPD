import base64
import io
import os
import random
import time
import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Kinetic Gears",
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

# Custom CSS for Glassmorphism login, layouts, and compact top padding
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

        /* Remove excess top padding above header */
        .block-container {{
            padding-top: 1.75rem !important;
            padding-bottom: 1.5rem !important;
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

# Helper to generate randomized arithmetic CAPTCHA
def generate_captcha():
    op = random.choice(['+', '-', '*', '/'])
    if op == '+':
        n1 = random.randint(1, 20)
        n2 = random.randint(1, 20)
        ans = n1 + n2
        question = f"{n1} + {n2}"
    elif op == '-':
        n1 = random.randint(1, 20)
        n2 = random.randint(1, n1)  # Keeps subtraction result non-negative
        ans = n1 - n2
        question = f"{n1} - {n2}"
    elif op == '*':
        n1 = random.randint(1, 10)
        n2 = random.randint(1, 10)
        ans = n1 * n2
        question = f"{n1} × {n2}"
    else:  # '/'
        n2 = random.randint(1, 10)
        ans = random.randint(1, 10)
        n1 = n2 * ans  # Ensures clean division without remainders
        question = f"{n1} ÷ {n2}"
    return question, ans

if "captcha_question" not in st.session_state:
    q, a = generate_captcha()
    st.session_state["captcha_question"] = q
    st.session_state["captcha_answer"] = a


def login_screen():
    st.markdown("<br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1.2, 1])

    with col2:
       with st.form("login_form"):
            if logo_base64:
                st.markdown(
                    f"""
                    <div style="text-align: center; margin-bottom: 0px;">
                        <img src="data:image/png;base64,{logo_base64}" width="80" style="display: block; margin: 0 auto;" />
                    </div>
                """,
                    unsafe_allow_html=True,
                )

            st.markdown(
                """
                <div style="text-align: center; margin-top: 4px; margin-bottom: 4px; margin-left: 50px; margin-right: 20px">
                    <h1 style="margin: 0; font-size: 50px; color: #ffffff; letter-spacing: 2px; font-weight: 800; line-height: 0.5;">KINETIC GEARS</h1>
                </div>
                <div style="text-align: center; margin-bottom: 10px;">
                    <h2 style='margin: 0; color: white; font-weight: 500; font-size: 16px; line-height: 0.5;'>Login, solve maths and start your work !</h2>
                </div>
                """,
                unsafe_allow_html=True,
            )
            username_input = st.text_input("Username", placeholder="Enter username")
            password_input = st.text_input("Password", type="password", placeholder="Enter password")
            
            # Arithmetic CAPTCHA Field as text input to remove stepper buttons
            captcha_input_str = st.text_input(
                f"Solve CAPTCHA: What is {st.session_state['captcha_question']}?",
                placeholder="Enter answer"
            )

            submit_button = st.form_submit_button("Log in", use_container_width=True)

            if submit_button:
                try:
                    captcha_input = int(captcha_input_str.strip())
                except ValueError:
                    captcha_input = None

                if captcha_input != st.session_state["captcha_answer"]:
                    st.error("Incorrect CAPTCHA answer. Please try again.")
                    # Regenerate CAPTCHA on failure
                    q, a = generate_captcha()
                    st.session_state["captcha_question"] = q
                    st.session_state["captcha_answer"] = a
                elif (
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
                    # Regenerate CAPTCHA on failure
                    q, a = generate_captcha()
                    st.session_state["captcha_question"] = q
                    st.session_state["captcha_answer"] = a


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
# Background session timeout listener script
st.markdown(
    f"""
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

        function checkExpiry() {{
            const now = Date.now();
            const elapsed = now - lastActivity;
            if ((timeoutDuration - elapsed) <= 0) {{
                window.location.href = "?do_logout=true";
            }}
        }}
        setInterval(checkExpiry, 1000);
    </script>
    """,
    unsafe_allow_html=True
)

username_val = st.session_state['username']
role_val = st.session_state['role']

# Render header using clean markdown and flexbox layout
st.markdown(
    f"""
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&display=swap" rel="stylesheet">
    <style>
        .custom-header-container {{
            display: flex;
            justify-content: flex-end;
            align-items: flex-end;
            flex-direction: column;
            width: 100%;
            margin-bottom: 10px;
        }}
        .clock-card {{
            background: linear-gradient(135deg, #e91e63, #c2185b);
            border-radius: 12px;
            padding: 6px 14px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(233, 30, 99, 0.3);
            font-family: 'Orbitron', sans-serif;
            margin-bottom: 6px;
        }}
        .time-display {{
            font-size: 16px;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: 1.5px;
        }}
        .date-display {{
            font-size: 10px;
            font-weight: 500;
            color: #fce4ec;
            letter-spacing: 0.5px;
        }}
        .user-logout-row {{
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 12px;
        }}
        .user-info {{
            color: white;
            font-family: sans-serif;
            font-size: 13px;
            text-align: right;
            line-height: 1.2;
        }}
        .logout-btn {{
            display: flex; align-items: center; background-color: #f44336; color: white;
            text-decoration: none; border-radius: 30px; width: 38px; height: 38px;
            overflow: hidden; box-shadow: 0 4px 15px rgba(244, 67, 54, 0.4);
            transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.3s ease;
            cursor: pointer; white-space: nowrap; flex-shrink: 0;
        }}
        .logout-btn:hover {{ width: 125px; background-color: #d32f2f; }}
        .logout-icon {{ min-width: 38px; height: 38px; display: flex; align-items: center; justify-content: center; }}
        .logout-icon svg {{ width: 20px; height: 20px; fill: none; stroke: white; stroke-width: 2.5; stroke-linecap: round; stroke-linejoin: round; }}
        .logout-text {{ font-family: sans-serif; font-weight: 600; font-size: 13px; padding-left: 2px; padding-right: 12px; opacity: 0; transition: opacity 0.3s ease 0.1s; }}
        .logout-btn:hover .logout-text {{ opacity: 1; }}
    </style>
    
    <div class="custom-header-container">
        <div class="clock-card">
            <div id="live-clock-time" class="time-display">00:00:00 AM</div>
            <div id="live-clock-date" class="date-display">Loading date...</div>
        </div>
        <div class="user-logout-row">
            <div class="user-info">
                👤 <b>{username_val}</b> | Role: <b>{role_val}</b>
            </div>
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
    </div>
    
    <script>
        function updateLiveClock() {{
            const now = new Date();
            let hours = now.getHours();
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const seconds = String(now.getSeconds()).padStart(2, '0');
            const ampm = hours >= 12 ? 'PM' : 'AM';
            hours = hours % 12;
            hours = hours ? hours : 12; 
            const formattedHours = String(hours).padStart(2, '0');
            const timeEl = document.getElementById('live-clock-time');
            const dateEl = document.getElementById('live-clock-date');
            if (timeEl) timeEl.innerText = formattedHours + ":" + minutes + ":" + seconds + " " + ampm;
            if (dateEl) {{
                const options = {{ weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' }};
                dateEl.innerText = now.toLocaleDateString('en-US', options);
            }}
        }}
        setInterval(updateLiveClock, 1000);
        updateLiveClock();
    </script>
    """,
    unsafe_allow_html=True
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
