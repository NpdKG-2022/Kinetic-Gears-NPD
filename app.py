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

# Custom CSS for Glassmorphism login, layouts, and Enterprise Styled Tabs
st.markdown(
    """
    <style>
        /* Full page background with clean dark theme */
        .stApp {
            background: linear-gradient(135deg, #0f0c1d 0%, #1a1532 100%);
            background-attachment: fixed;
        }

        /* Remove excess top padding above header */
        .block-container {
            padding-top: 1.75rem !important;
            padding-bottom: 1.5rem !important;
        }

        /* --- ENTERPRISE STYLED TABS --- */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: rgba(0, 0, 0, 0.2);
            padding: 10px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .stTabs [data-baseweb="tab"] {
            height: 45px;
            background-color: rgba(255, 255, 255, 0.08);
            border-radius: 8px;
            color: rgba(255, 255, 255, 0.85);
            font-weight: 600;
            padding: 0 20px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            transition: all 0.3s ease;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background-color: rgba(255, 255, 255, 0.18);
            color: #ffffff;
        }
        .stTabs [aria-selected="true"] {
            background-color: #1e88e5 !important;
            color: #ffffff !important;
            border: 1px solid #1e88e5 !important;
            box-shadow: 0 4px 15px rgba(30, 136, 229, 0.4);
        }

        /* --- GLASSMORPHISM LOGIN FORM STYLING --- */
        div[data-testid="stForm"] {
            background: rgba(255, 255, 255, 0.08) !important;
            backdrop-filter: blur(16px) saturate(180%) !important;
            -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 24px !important;
            padding: 40px 30px !important;
            box-shadow: 0 30px 60px rgba(0, 0, 0, 0.4) !important;
        }

        div[data-testid="stTextInput"] input {
            background-color: transparent !important;
            border: none !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.5) !important;
            border-radius: 0px !important;
            color: #ffffff !important;
            padding: 10px 5px !important;
            font-size: 15px !important;
        }
        div[data-testid="stTextInput"] input:focus {
            border-bottom: 2px solid #ffffff !important;
            box-shadow: none !important;
        }
        div[data-testid="stTextInput"] label {
            color: rgba(255, 255, 255, 0.9) !important;
            font-weight: 500 !important;
        }

        div[data-testid="stFormSubmitButton"] button {
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
        }
        div[data-testid="stFormSubmitButton"] button:hover {
            background-color: #f0f0f0 !important;
            transform: translateY(-2px);
        }

        /* Make dataframes take full width and wrap cleanly */
        [data-testid="stDataFrame"] {
            width: 100% !important;
        }
        [data-testid="stDataFrame"] > div {
            width: 100% !important;
        }
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

# Load dataset helper
CUSTOM_ITEMS_FILE = "custom_items.csv"
months_list = ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]

if os.path.exists(CUSTOM_ITEMS_FILE):
    df_tracker = pd.read_csv(CUSTOM_ITEMS_FILE)
else:
    df_tracker = pd.DataFrame(columns=["Plant", "CODE NO.", "ITEM NAME", "PRICE", "Drawing"] + months_list)

if os.path.exists(DRAWINGS_MAP_FILE):
    df_drawings = pd.read_csv(DRAWINGS_MAP_FILE)
    if not df_drawings.empty and not df_tracker.empty:
        df_tracker = pd.merge(df_tracker, df_drawings, on="CODE NO.", how="left", suffixes=("", "_map"))
        if "Drawing_map" in df_tracker.columns:
            df_tracker["Drawing"] = df_tracker["Drawing_map"].combine_first(
                df_tracker.get("Drawing", pd.Series([None] * len(df_tracker)))
            )
            df_tracker = df_tracker.drop(columns=[c for c in df_tracker.columns if "_map" in c])

if "Drawing" not in df_tracker.columns:
    df_tracker["Drawing"] = ""

# ================= ENTERPRISE STYLED TABS =================
tab1, tab2 = st.tabs(["🔍 View Drawing (In-Browser)", "📐 Manage Drawings"])

# ================= TAB 1: VIEW DRAWING =================
with tab1:
    st.subheader("🔍 In-Browser Engineering Drawing Viewer")
    v_col1, v_col2 = st.columns(2)

    all_codes = sorted(df_tracker["CODE NO."].astype(str).unique().tolist()) if not df_tracker.empty and "CODE NO." in df_tracker.columns else []
    all_items = sorted(df_tracker["ITEM NAME"].astype(str).unique().tolist()) if not df_tracker.empty and "ITEM NAME" in df_tracker.columns else []

    with v_col1:
        search_by_code = st.selectbox("Select by Code No.", options=["-- Select --"] + all_codes, key="draw_search_code")
    with v_col2:
        search_by_item = st.selectbox("Select by Item Name", options=["-- Select --"] + all_items, key="draw_search_item")

    matched_rows = pd.DataFrame()
    if search_by_code != "-- Select --":
        matched_rows = df_tracker[df_tracker["CODE NO."].astype(str) == search_by_code]
    elif search_by_item != "-- Select --":
        matched_rows = df_tracker[df_tracker["ITEM NAME"].astype(str) == search_by_item]

    if not matched_rows.empty:
        row = matched_rows.iloc[0]
        c_code = row.get("CODE NO.", "")
        c_item = row.get("ITEM NAME", "")
        c_plant = row.get("Plant", "General")
        drawing_path = row.get("Drawing", "")

        st.markdown("---")
        st.info(f"**Plant:** {c_plant} | **Code No:** `{c_code}` | **Item Name:** `{c_item}`")

        if pd.notna(drawing_path) and str(drawing_path).strip() != "" and os.path.exists(str(drawing_path)):
            st.success("Drawing loaded successfully in viewer:")
            if drawing_path.lower().endswith((".png", ".jpg", ".jpeg", ".tiff", ".tif", ".svg")):
                st.image(drawing_path, caption=f"Drawing: {c_code} - {c_item}", use_column_width=True)
            elif drawing_path.lower().endswith(".pdf"):
                with open(drawing_path, "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode("utf-8")
                pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="700px" type="application/pdf">'
                st.markdown(pdf_display, unsafe_allow_html=True)
                
                # Admin-only download button restriction
                if role_val == "Admin":
                    st.markdown("<br>", unsafe_allow_html=True)
                    with open(drawing_path, "rb") as pdf_file:
                        PDFbyte = pdf_file.read()
                    st.download_button(label="📥 Download Drawing PDF", data=PDFbyte, file_name=os.path.basename(drawing_path), mime='application/pdf')
                else:
                    st.info("🔒 Download restricted to Administrator accounts only.")
        else:
            st.warning("No drawing file attached to this item. Go to **'Manage Drawings'** tab to upload one.")
    else:
        st.info("Please select a Code No. or Item Name above to view its drawing.")


# ================= TAB 2: MANAGE DRAWINGS =================
with tab2:
    st.subheader("📐 Add or Update Drawings with Part Details")
    
    with st.form("drawing_manager_form"):
        manual_code = st.text_input("Enter Part Number", placeholder="e.g. PM-001")
        manual_item_name = st.text_input("Enter Part Name", placeholder="e.g. Gear Blank")

        uploaded_file = st.file_uploader("Upload Drawing File (PDF, PNG, JPG, TIFF)", type=["pdf", "png", "jpg", "jpeg", "tiff", "tif"])
        drawing_submitted = st.form_submit_button("Save Drawing & Part Details")

        if drawing_submitted:
            if not manual_code.strip() or not manual_item_name.strip():
                st.error("Please provide both a valid Part Number and Part Name.")
            elif uploaded_file is None:
                st.error("Please upload a drawing file first.")
            else:
                file_save_path = os.path.join(DRAWINGS_DIR, uploaded_file.name)
                with open(file_save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # 1. Update/Save drawing map file
                df_d_map = pd.read_csv(DRAWINGS_MAP_FILE) if os.path.exists(DRAWINGS_MAP_FILE) else pd.DataFrame(columns=["CODE NO.", "Drawing"])
                df_d_map = df_d_map[df_d_map["CODE NO."].astype(str) != str(manual_code.strip())]
                
                updated_map = pd.concat([df_d_map, pd.DataFrame({"CODE NO.": [manual_code.strip()], "Drawing": [file_save_path]})], ignore_index=True)
                updated_map.to_csv(DRAWINGS_MAP_FILE, index=False)

                # 2. Update/Save custom items tracker dataframe
                if os.path.exists(CUSTOM_ITEMS_FILE):
                    df_custom = pd.read_csv(CUSTOM_ITEMS_FILE)
                else:
                    df_custom = pd.DataFrame(columns=["Plant", "CODE NO.", "ITEM NAME", "PRICE", "Drawing"] + months_list)

                # Check if code already exists in custom items, update it; otherwise append new row
                if not df_custom.empty and "CODE NO." in df_custom.columns and str(manual_code.strip()) in df_custom["CODE NO."].astype(str).values:
                    df_custom.loc[df_custom["CODE NO."].astype(str) == str(manual_code.strip()), "ITEM NAME"] = manual_item_name.strip().upper()
                    df_custom.loc[df_custom["CODE NO."].astype(str) == str(manual_code.strip()), "Drawing"] = file_save_path
                else:
                    new_row_data = {
                        "Plant": ["General"],
                        "CODE NO.": [manual_code.strip()],
                        "ITEM NAME": [manual_item_name.strip().upper()],
                        "PRICE": [0.0],
                        "Drawing": [file_save_path],
                    }
                    for m in months_list:
                        new_row_data[m] = [0]
                    df_new_row = pd.DataFrame(new_row_data)
                    df_custom = pd.concat([df_custom, df_new_row], ignore_index=True)

                df_custom.to_csv(CUSTOM_ITEMS_FILE, index=False)
                st.success(f"Successfully saved drawing and registered Part No: `{manual_code}` ({manual_item_name})!")
                st.rerun()
