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
    initial_sidebar_state="collapsed"
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
    "user": {"password": "user123", "role": "User"},
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
        n2 = random.randint(1, n1)
        ans = n1 - n2
        question = f"{n1} - {n2}"
    elif op == '*':
        n1 = random.randint(1, 10)
        n2 = random.randint(1, 10)
        ans = n1 * n2
        question = f"{n1} × {n2}"
    else:
        n2 = random.randint(1, 10)
        ans = random.randint(1, 10)
        n1 = n2 * ans
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
                <div style="text-align: center; margin-bottom: 10px; margin-left: 50px; margin-right: 20px">
                    <h2 style='margin: 0; color: white; font-weight: 500; font-size: 16px; line-height: 0.5;'>Login, solve maths and start your work !</h2>
                </div>
                """,
                unsafe_allow_html=True,
            )
            username_input = st.text_input("Username", placeholder="Enter username")
            password_input = st.text_input("Password", type="password", placeholder="Enter password")
            
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
                    q, a = generate_captcha()
                    st.session_state["captcha_question"] = q
                    st.session_state["captcha_answer"] = a


if not st.session_state.get("logged_in", False):
    login_screen()
    st.stop()

username_val = st.session_state.get('username', '')
role_val = st.session_state.get('role', '')

# ================= PROFESSIONAL SIDEBAR WITH LOGO & USER DETAILS =================
with st.sidebar:
    if logo_base64:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 10px 0 10px 0;">
                <img src="data:image/png;base64,{logo_base64}" width="65" style="display: block; margin: 0 auto 10px auto;" />
                <h3 style="margin: 0; font-size: 18px; color: #ffffff; letter-spacing: 1px;">KINETIC GEARS</h3>
                <p style="margin: 2px 0 0 0; font-size: 11px; color: rgba(255,255,255,0.6);">Drawing Management System</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("---")
    
    st.markdown(
        f"""
        <div style="padding: 5px 10px; margin-bottom: 10px;">
            <div style="font-size: 14px; color: #ffffff; font-weight: 600; margin-bottom: 4px;">
                👤 {username_val}
            </div>
            <div style="font-size: 13px; color: rgba(255,255,255,0.8);">
                Role: <b style="color: #ffffff;">{role_val}</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True
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

st.components.v1.html(
    """
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&display=swap" rel="stylesheet">
    <style>
        body { margin: 0; background-color: transparent; display: flex; justify-content: flex-end; }
        .clock-card {
            background: linear-gradient(135deg, #e91e63, #c2185b);
            border-radius: 10px;
            padding: 5px 10px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(233, 30, 99, 0.3);
            font-family: 'Orbitron', sans-serif;
            display: inline-block;
        }
        .time-display {
            font-size: 20px;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: 1px;
        }
        .date-display {
            font-size: 12px;
            color: #fce4ec;
        }
    </style>
    <div class="clock-card">
        <div id="futuristic-time" class="time-display">00:00:00 AM</div>
        <div id="futuristic-date" class="date-display">Loading...</div>
    </div>
    <script>
        function updateFuturisticClock() {
            const now = new Date();
            let hours = now.getHours();
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const seconds = String(now.getSeconds()).padStart(2, '0');
            const ampm = hours >= 12 ? 'PM' : 'AM';
            hours = hours % 12 || 12;
            document.getElementById('futuristic-time').innerText = `${String(hours).padStart(2, '0')}:${minutes}:${seconds} ${ampm}`;
            document.getElementById('futuristic-date').innerText = now.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });
        }
        setInterval(updateFuturisticClock, 1000);
        updateFuturisticClock();
    </script>
    """,
    height=60,
)

DRAWINGS_MAP_FILE = "item_drawings.csv"
DRAWINGS_DIR = "drawings"

os.makedirs(DRAWINGS_DIR, exist_ok=True)

    if os.path.exists(DRAWINGS_MAP_FILE):
        df_drawings = pd.read_csv(DRAWINGS_MAP_FILE)
        if not df_drawings.empty:
            df = pd.merge(df, df_drawings, on="CODE NO.", how="left", suffixes=("", "_map"))
            if "Drawing_map" in df.columns:
                df["Drawing"] = df["Drawing_map"].combine_first(
                    df.get("Drawing", pd.Series([None] * len(df)))
                )
                df = df.drop(columns=[c for c in df.columns if "_map" in c])

    if "Drawing" not in df.columns:
        df["Drawing"] = ""

    df["Total_Schedule"] = df[months_list].sum(axis=1)
    return df 

    # ================= CARD GRID NAVIGATION MENU =================
    st.markdown("### 📌 Navigation Menu")

    tabs_config = [
        {"title": "View Drawing (In-Browser)", "icon": "🔍", "bg": "#e0f7fa", "color": "#00838f"},
        {"title": "Manage Drawings", "icon": "📐", "bg": "#e8f5e9", "color": "#2e7d32"},
    ]

    cols = st.columns(5)
    for i, tab in enumerate(tabs_config):
        with cols[i]:
            tab_full_name = f"{tab['icon']}\n{tab['title']}"
            if st.button(tab_full_name, key=f"nav_btn_{i}", use_container_width=True):
                st.session_state["selected_tab"] = f"{tab['icon']} {tab['title']}"
                st.rerun()

    st.markdown("---")
    selected_tab = st.session_state["selected_tab"]

  
    # ================= TAB 1: VIEW DRAWING =================
    elif selected_tab == "🔍 View Drawing (In-Browser)":
        st.subheader("🔍 In-Browser Engineering Drawing Viewer")
        v_col1, v_col2 = st.columns(2)

        all_codes = sorted(df_tracker["CODE NO."].astype(str).unique().tolist())
        all_items = sorted(df_tracker["ITEM NAME"].astype(str).unique().tolist())

        with v_col1:
            search_by_code = st.selectbox(
                "Select by Code No.",
                options=["-- Select --"] + all_codes,
                key="draw_search_code",
            )
        with v_col2:
            search_by_item = st.selectbox(
                "Select by Item Name",
                options=["-- Select --"] + all_items,
                key="draw_search_item",
            )

        matched_rows = pd.DataFrame()
        if search_by_code != "-- Select --":
            matched_rows = df_tracker[df_tracker["CODE NO."].astype(str) == search_by_code]
        elif search_by_item != "-- Select --":
            matched_rows = df_tracker[df_tracker["ITEM NAME"].astype(str) == search_by_item]

        if not matched_rows.empty:
            row = matched_rows.iloc[0]
            c_code = row["CODE NO."]
            c_item = row["ITEM NAME"]
            c_plant = row["Plant"]
            drawing_path = row.get("Drawing", "")

            st.markdown("---")
            st.info(
                f"**Plant:** {c_plant} | **Code No:** `{c_code}` | **Item Name:** `{c_item}`"
            )

            if (
                pd.notna(drawing_path)
                and str(drawing_path).strip() != ""
                and os.path.exists(str(drawing_path))
            ):
                st.success("Drawing loaded successfully in viewer:")
                if drawing_path.lower().endswith((".png", ".jpg", ".jpeg")):
                    st.image(
                        drawing_path,
                        caption=f"Drawing: {c_code} - {c_item}",
                        use_container_width=True,
                    )
                elif drawing_path.lower().endswith(".pdf"):
                    with open(drawing_path, "rb") as f:
                        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
                    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="700px" type="application/pdf"></iframe>'
                    st.markdown(pdf_display, unsafe_allow_html=True)
            else:
                st.warning(
                    "No drawing file attached to this item. Go to **'Manage Drawings'** tab to upload one."
                )
        else:
            st.info("Please select a Code No. or Item Name above to view its drawing.")

   # ================= TAB 2: MANAGE DRAWINGS =================
    elif selected_tab == "📐 Manage Drawings":
        st.subheader("📐 Attach or Update Drawings for Code Numbers")
        all_unique_codes = sorted(
            df_tracker["CODE NO."].astype(str).unique().tolist()
        )

        with st.form("drawing_manager_form"):
            selected_code_for_drawing = st.selectbox(
                "Select Code No.", options=all_unique_codes
            )
            match_row = df_tracker[
                df_tracker["CODE NO."].astype(str) == selected_code_for_drawing
            ]
            if not match_row.empty:
                st.markdown(f"**Associated Item Name:** `{match_row.iloc[0]['ITEM NAME']}`")

            uploaded_file = st.file_uploader(
                "Upload Drawing File (PDF, PNG, JPG)",
                type=["pdf", "png", "jpg", "jpeg"],
            )
            drawing_submitted = st.form_submit_button("Save Drawing Link")

            if drawing_submitted:
                if uploaded_file is not None:
                    file_save_path = os.path.join(DRAWINGS_DIR, uploaded_file.name)
                    with open(file_save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    df_d_map = (
                        pd.read_csv(DRAWINGS_MAP_FILE)
                        if os.path.exists(DRAWINGS_MAP_FILE)
                        else pd.DataFrame(columns=["CODE NO.", "Drawing"])
                    )
                    df_d_map = df_d_map[
                        df_d_map["CODE NO."].astype(str)
                        != str(selected_code_for_drawing)
                    ]
                    pd.concat(
                        [
                            df_d_map,
                            pd.DataFrame({
                                "CODE NO.": [selected_code_for_drawing],
                                "Drawing": [file_save_path],
                            }),
                        ],
                        ignore_index=True,
                    ).to_csv(DRAWINGS_MAP_FILE, index=False)

                    st.success(
                        f"Successfully linked drawing to Code No: {selected_code_for_drawing}!"
                    )
                    st.rerun()
                else:
                    st.error("Please upload a drawing file first.")

