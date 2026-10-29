import base64
import io
import json
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

# Custom CSS for Glassmorphism login, layouts, and Sidebar Card Navigation
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

        /* --- SIDEBAR STYLING --- */
        [data-testid="stSidebar"] {
            background-color: #120e24 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.1);
            padding-top: 10px;
        }

        /* Custom Sidebar Navigation Button Styling */
        [data-testid="stSidebar"] div.stButton > button {
            background-color: rgba(255, 255, 255, 0.03) !important;
            color: rgba(255, 255, 255, 0.8) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 12px !important;
            width: 100% !important;
            text-align: left !important;
            padding: 10px 16px !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            box-shadow: none !important;
            transition: all 0.25s ease !important;
            margin-bottom: 6px !important;
        }
        [data-testid="stSidebar"] div.stButton > button:hover {
            background-color: rgba(255, 255, 255, 0.08) !important;
            color: #ffffff !important;
            border-color: rgba(255, 255, 255, 0.2) !important;
            transform: translateX(2px);
        }

        /* Active Sidebar Button Styling (highlighted red/accent or white) */
        [data-testid="stSidebar"] div.stButton > button[kind="secondary"] {
            /* Can be customized or left standard */
        }

        /* --- HOVER-EXPANDING RED LOGOUT BUTTON --- */
        .logout-icon-wrapper {
            position: relative;
            display: flex;
            align-items: center;
            justify-content: flex-start;
            float: center;
            margin-top: 5px;
            cursor: pointer;
        }
        .logout-icon-btn {
            background: #e53935;
            color: #ffffff;
            width: 38px;
            height: 38px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: flex-start;
            padding-left: 10px;
            box-shadow: 0 4px 10px rgba(229, 57, 53, 0.4);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            white-space: nowrap;
            overflow: hidden;
        }
        .logout-icon-wrapper:hover .logout-icon-btn {
            width: 115px;
            border-radius: 20px;
            padding-right: 5px;
            padding-left: 10px;
            justify-content: space-between;
        }
        .logout-text {
            opacity: 0;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.5px;
            transition: opacity 0.2s ease 0.1s;
            pointer-events: none;
        }
        .logout-icon-wrapper:hover .logout-text {
            opacity: 1;
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

# Handle logout trigger via query param
if st.query_params.get("do_logout") == "true":
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.session_state["role"] = ""
    st.session_state["login_time"] = 0.0
    st.query_params.clear()
    st.rerun()

# Initialize active navigation state if not present
if "nav_active" not in st.session_state:
    st.session_state["nav_active"] = "🏠 View Drawing"


# ================= REFERENCE-STYLE SIDEBAR NAVIGATION (NO RADIO) =================
with st.sidebar:
    if logo_base64:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 12px; padding: 5px 5px 15px 5px;">
                <img src="data:image/png;base64,{logo_base64}" width="38" style="display: block;" />
                <h2 style="margin: 0; font-size: 20px; color: #ffffff; font-weight: 700; letter-spacing: 0.5px;">Main Menu</h2>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("<hr style='margin: 0 0 15px 0; border: none; border-top: 1px solid rgba(255,255,255,0.15);'>", unsafe_allow_html=True)
    
    # Custom Sidebar Navigation Buttons (Pill Cards)
    if st.button("🏠 View Drawing", use_container_width=True):
        st.session_state["nav_active"] = "🏠 View Drawing"
        st.rerun()
        
    if st.button("📤 Manage Drawings", use_container_width=True):
        st.session_state["nav_active"] = "📤 Manage Drawings"
        st.rerun()
        
    if st.button("🧭 Route Cards", use_container_width=True):
        st.session_state["nav_active"] = "🧭 Route Cards"
        st.rerun()
        
    if st.button("📋 Documentation", use_container_width=True):
        st.session_state["nav_active"] = "📋 Documentation"
        st.rerun()

    st.markdown("---")
    
    st.markdown(
        f"""
        <div style="padding: 5px 5px; margin-bottom: 5px;">
            <div style="font-size: 13px; color: #ffffff; font-weight: 600; margin-bottom: 2px;">
                👤 {username_val}
            </div>
            <div style="font-size: 12px; color: rgba(255,255,255,0.7);">
                Role: <b style="color: #ffffff;">{role_val}</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    st.markdown("<p style='font-size: 11px; color: rgba(255,255,255,0.5); text-align: center;'>System operational & secure.</p>", unsafe_allow_html=True)

nav_selection = st.session_state["nav_active"]


# ================= TOP HEADER BAR & CLOCK WITH SIDE-BY-SIDE LOGOUT =================
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

top_col1, top_col2 = st.columns([2.25, 2.5])
with top_col2:
    header_cols = st.columns([3.2, 1])
    
    with header_cols[0]:
        st.markdown(
            """
            <div style="display: flex; align-items: center; height: 60px; justify-content: flex-end;">
                <div class="logout-icon-wrapper" style="margin-top: 0; float: none;">
                    <a href="?do_logout=true" target="_self" style="text-decoration: none;">
                        <div class="logout-icon-btn">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink: 0;">
                                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                                <polyline points="16 17 21 12 16 7"></polyline>
                                <line x1="21" y1="12" x2="9" y2="12"></line>
                            </svg>
                            <span class="logout-text">LOGOUT</span>
                        </div>
                    </a>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with header_cols[1]:
        st.components.v1.html(
            """
            <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&display=swap" rel="stylesheet">
            <style>
                body { margin: 0; background-color: transparent; display: flex; justify-content: flex-end; align-items: right; }
                .clock-card {
                    background: linear-gradient(135deg, #000080, #4169E1);
                    border-radius: 10px;
                    padding: 5px 10px;
                    text-align: center;
                    box-shadow: 0 2px 10px rgba(233, 30, 99, 0.3);
                    font-family: 'Orbitron', sans-serif;
                    display: inline-block;
                    float: right;
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
CUSTOM_ITEMS_FILE = "custom_items.csv"
DRAWINGS_DIR = "drawings"

os.makedirs(DRAWINGS_DIR, exist_ok=True)
months_list = ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]

# 1. Load custom items tracker dataset
if os.path.exists(CUSTOM_ITEMS_FILE):
    df_tracker = pd.read_csv(CUSTOM_ITEMS_FILE)
    if "CODE NO." in df_tracker.columns:
        df_tracker = df_tracker.rename(columns={"CODE NO.": "PART NO."})
    if "ITEM NAME" in df_tracker.columns:
        df_tracker = df_tracker.rename(columns={"ITEM NAME": "PART NAME"})
else:
    df_tracker = pd.DataFrame(columns=["Plant", "PART NO.", "PART NAME", "PRICE", "Drawing"] + months_list)

if "Drawing" not in df_tracker.columns:
    df_tracker["Drawing"] = ""

# 2. Load and merge drawings map dataset
if os.path.exists(DRAWINGS_MAP_FILE):
    df_drawings = pd.read_csv(DRAWINGS_MAP_FILE)
    if "Item Code" in df_drawings.columns and "PART NO." not in df_drawings.columns:
        df_drawings = df_drawings.rename(columns={"Item Code": "PART NO."})
    if "CODE NO." in df_drawings.columns and "PART NO." not in df_drawings.columns:
        df_drawings = df_drawings.rename(columns={"CODE NO.": "PART NO."})
    if "Drawing File" in df_drawings.columns and "Drawing" not in df_drawings.columns:
        df_drawings = df_drawings.rename(columns={"Drawing File": "Drawing"})
        
    if not df_drawings.empty and "PART NO." in df_drawings.columns:
        drawing_dict = pd.Series(df_drawings.Drawing.values, index=df_drawings["PART NO."].astype(str)).to_dict()
        df_tracker["PART_STR"] = df_tracker["PART NO."].astype(str)
        df_tracker["Drawing"] = df_tracker["PART_STR"].map(drawing_dict).combine_first(df_tracker["Drawing"])
        df_tracker = df_tracker.drop(columns=["PART_STR"])



# ================= VIEW 1: VIEW DRAWING =================
if nav_selection == "🏠 View Drawing":
    st.subheader("🔍 In-Browser Engineering Drawing Viewer")
    
    main_search_col, _ = st.columns([3, 1])

    with main_search_col:
        r_col1, r_col2, r_col3 = st.columns([1.5, 1.5, 3])

        with r_col1:
            st.markdown("<p style='font-size: 14px; font-weight: 600; padding-top: 8px; margin-bottom: 0;'>Search Drawing By:</p>", unsafe_allow_html=True)

        with r_col2:
            search_mode = st.radio("Search Mode", ["Part No.", "Part Name"], horizontal=True, label_visibility="collapsed")

        with r_col3:
            target_col = "PART NO." if search_mode == "Part No." else "PART NAME"
            all_options = sorted(df_tracker[target_col].astype(str).unique().tolist()) if not df_tracker.empty and target_col in df_tracker.columns else []
            
            selected_value = st.selectbox(
                "Google Search Bar",
                options=[""] + all_options,
                format_func=lambda x: f"🔍 Type or search {search_mode}..." if x == "" else x,
                label_visibility="collapsed",
                key=f"google_search_{search_mode}"
            )

    matched_rows = pd.DataFrame()
    if selected_value and selected_value.strip() != "":
        matched_rows = df_tracker[df_tracker[target_col].astype(str) == selected_value]

    if not matched_rows.empty:
        row = matched_rows.iloc[0]
        c_code = row.get("PART NO.", "")
        c_item = row.get("PART NAME", "")
        drawing_path = row.get("Drawing", "")

        st.markdown(f"<div style='margin-top: -10px; margin-bottom: 10px;'><b>Part No:</b> <code>{c_code}</code> &nbsp;|&nbsp; <b>Part Name:</b> <code>{c_item}</code></div>", unsafe_allow_html=True)

        if pd.notna(drawing_path) and str(drawing_path).strip() != "" and os.path.exists(str(drawing_path)):
            if drawing_path.lower().endswith((".png", ".jpg", ".jpeg", ".tiff", ".tif", ".svg")):
                st.image(drawing_path, caption=f"Drawing: {c_code} - {c_item}", use_container_width=True)
            elif drawing_path.lower().endswith(".pdf"):
                preview_img_path = drawing_path.rsplit(".", 1)[0] + "_preview.png"
                
                if os.path.exists(preview_img_path):
                    st.image(preview_img_path, caption=f"Drawing: {c_code} - {c_item} (Click fullscreen icon top-right to zoom)", use_container_width=True)
                else:
                    try:
                        import fitz  # PyMuPDF
                        doc = fitz.open(drawing_path)
                        for page_num in range(len(doc)):
                            page = doc.load_page(page_num)
                            pix = page.get_pixmap(dpi=300)
                            img_bytes = pix.tobytes("png")
                            st.image(img_bytes, caption=f"Drawing: {c_code} - {c_item} (Page {page_num + 1})", use_container_width=True)
                    except Exception:
                        st.info("📄 PDF drawing attached.")

                if role_val == "Admin":
                    st.markdown("<br>", unsafe_allow_html=True)
                    with open(drawing_path, "rb") as pdf_file:
                        PDFbyte = pdf_file.read()
                    st.download_button(label="📥 Download Drawing PDF", data=PDFbyte, file_name=os.path.basename(drawing_path), mime='application/pdf')
                else:
                    st.info("🔒 Download restricted to Administrator accounts only.")
        else:
            st.warning("No drawing file attached to this item. Go to **'Manage Drawings'** from the sidebar to upload one.")
    else:
        st.info(f"Type or select a {search_mode} above to instantly view your drawing")


# ================= VIEW 2: MANAGE DRAWINGS =================
elif nav_selection == "📤 Manage Drawings":
    st.subheader("📐 Add or Update Drawings with Part Details")
    
    if "drawing_upload_success" not in st.session_state:
        st.session_state["drawing_upload_success"] = None

    if st.session_state["drawing_upload_success"]:
        st.success(st.session_state["drawing_upload_success"])
        st.session_state["drawing_upload_success"] = None

    with st.form("drawing_manager_form", clear_on_submit=True):
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            manual_code = st.text_input("Enter Part Number *", placeholder="e.g. PM-001")
        with col_p2:
            manual_item_name = st.text_input("Enter Part Name *", placeholder="e.g. Gear Blank")

        up_col1, _ = st.columns([1, 2])
        with up_col1:
            uploaded_file = st.file_uploader("Upload Drawing File (PDF, PNG, JPG, TIFF) *", type=["pdf", "png", "jpg", "jpeg", "tiff", "tif"])

        drawing_submitted = st.form_submit_button("Save Drawing & Part Details")

        if drawing_submitted:
            if not manual_code.strip() or not manual_item_name.strip() or uploaded_file is None:
                st.error("⚠️ All fields (Part Number, Part Name, and Drawing File) are mandatory!")
            else:
                file_save_path = os.path.join(DRAWINGS_DIR, uploaded_file.name)
                with open(file_save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                if uploaded_file.name.lower().endswith(".pdf"):
                    try:
                        import fitz  # PyMuPDF
                        doc = fitz.open(file_save_path)
                        page = doc.load_page(0)
                        pix = page.get_pixmap(dpi=300)
                        preview_img_path = file_save_path.rsplit(".", 1)[0] + "_preview.png"
                        pix.save(preview_img_path)
                    except Exception:
                        pass

                if os.path.exists(DRAWINGS_MAP_FILE):
                    df_d_map = pd.read_csv(DRAWINGS_MAP_FILE)
                    if "Item Code" in df_d_map.columns and "PART NO." not in df_d_map.columns:
                        df_d_map = df_d_map.rename(columns={"Item Code": "PART NO."})
                    if "CODE NO." in df_d_map.columns and "PART NO." not in df_d_map.columns:
                        df_d_map = df_d_map.rename(columns={"CODE NO.": "PART NO."})
                    if "Drawing File" in df_d_map.columns and "Drawing" not in df_d_map.columns:
                        df_d_map = df_d_map.rename(columns={"Drawing File": "Drawing"})
                else:
                    df_d_map = pd.DataFrame(columns=["PART NO.", "Drawing"])

                if "PART NO." in df_d_map.columns:
                    df_d_map = df_d_map[df_d_map["PART NO."].astype(str) != str(manual_code.strip())]
                
                updated_map = pd.concat([df_d_map, pd.DataFrame({"PART NO.": [manual_code.strip()], "Drawing": [file_save_path]})], ignore_index=True)
                updated_map.to_csv(DRAWINGS_MAP_FILE, index=False)

                if os.path.exists(CUSTOM_ITEMS_FILE):
                    df_custom = pd.read_csv(CUSTOM_ITEMS_FILE)
                    if "CODE NO." in df_custom.columns:
                        df_custom = df_custom.rename(columns={"CODE NO.": "PART NO."})
                    if "ITEM NAME" in df_custom.columns:
                        df_custom = df_custom.rename(columns={"ITEM NAME": "PART NAME"})
                else:
                    df_custom = pd.DataFrame(columns=["Plant", "PART NO.", "PART NAME", "PRICE", "Drawing"] + months_list)

                if not df_custom.empty and "PART NO." in df_custom.columns and str(manual_code.strip()) in df_custom["PART NO."].astype(str).values:
                    df_custom.loc[df_custom["PART NO."].astype(str) == str(manual_code.strip()), "PART NAME"] = manual_item_name.strip().upper()
                    df_custom.loc[df_custom["PART NO."].astype(str) == str(manual_code.strip()), "Drawing"] = file_save_path
                else:
                    new_row_data = {
                        "Plant": ["General"],
                        "PART NO.": [manual_code.strip()],
                        "PART NAME": [manual_item_name.strip().upper()],
                        "PRICE": [0.0],
                        "Drawing": [file_save_path],
                    }
                    for m in months_list:
                        new_row_data[m] = [0]
                    df_new_row = pd.DataFrame(new_row_data)
                    df_custom = pd.concat([df_custom, df_new_row], ignore_index=True)

                df_custom.to_csv(CUSTOM_ITEMS_FILE, index=False)
                
                st.session_state["drawing_upload_success"] = f"✅ Drawing uploaded successfully and Part No: `{manual_code}` ({manual_item_name}) registered!"
                st.rerun()


# ================= VIEW 3: ROUTE CARDS =================
elif nav_selection == "🧭 Route Cards":
    st.subheader("🧭 Shop-Floor Route Card & Operation System")
    
    ROUTE_CARDS_FILE = "route_cards_data.csv"
    
    operation_master = [
        "Incoming Inspection", "Pre-Final Inspection", "No-PASS Inspection", 
        "Inspection Before HT", "Firewall Inspection", "Parting", 
        "CNC Turning", "CNC Hobbing", "VMC Milling", "Heat Treatment (HT)", 
        "Surface Grinding", "Cylindrical Grinding", "Deburring & Cleaning", "Final Quality Inspection"
    ]

    if os.path.exists(ROUTE_CARDS_FILE):
        df_rc = pd.read_csv(ROUTE_CARDS_FILE)
    else:
        df_rc = pd.DataFrame(columns=[
            "RC No", "Part No", "Part Name", "RM Issue Slip", "RM Qty", "RM Issue Date",
            "Batch No", "Process Steps JSON", "Status", "Created Date"
        ])

    rc_action = st.radio("Select Action", ["Create New Route Card", "View / Update Existing Route Cards"], horizontal=True)
    
    if rc_action == "Create New Route Card":
        st.markdown("### 📝 Generate New Route Card")
        
        with st.form("create_rc_form"):
            st.markdown("<p style='font-weight: 600; margin-bottom: 2px;'>Route Card No. *</p>", unsafe_allow_html=True)
            r_c_col1, r_c_col2, _ = st.columns([0.1, 0.9, 2])
            with r_c_col1:
                st.markdown("<div style='padding-top: 10px; font-weight: 700; font-size: 16px; color: #ffffff;'>RC-</div>", unsafe_allow_html=True)
            with r_c_col2:
                rc_number_suffix = st.text_input("RC Suffix", value="", placeholder="Enter Route Card No.", label_visibility="collapsed")
            
            st.markdown("<br>", unsafe_allow_html=True)

            p_col1, p_col2 = st.columns(2)
            with p_col1:
                available_parts = df_tracker["PART NO."].astype(str).unique().tolist() if not df_tracker.empty else []
                selected_part_no = st.selectbox("Select Part No. *", options=[""] + available_parts)
            
            auto_part_name = ""
            if selected_part_no and selected_part_no != "":
                matched_p = df_tracker[df_tracker["PART NO."].astype(str) == selected_part_no]
                if not matched_p.empty:
                    auto_part_name = matched_p.iloc[0].get("PART NAME", "")
            
            with p_col2:
                part_name_input = st.text_input("Part Name *", value=auto_part_name, placeholder="e.g. WASHER / GEAR BLANK")

            rm_col1, rm_col2, rm_col3, rm_col4 = st.columns(4)
            with rm_col1:
                rm_qty_input = st.text_input("RM Issued Qty *", placeholder="Enter issued qty")
            with rm_col2:
                rm_issue_slip = st.text_input("RM Issue Slip No.", placeholder="Enter Issue Slip No.")
            with rm_col3:
                import datetime
                rm_issue_date = st.date_input(
                    "RM Issue Date (DD/MM/YYYY) *", 
                    value=datetime.date.today(), 
                    min_value=datetime.date(2000, 4, 1), 
                    max_value=datetime.date(2999, 3, 31),
                    format="DD/MM/YYYY"
                )
            with rm_col4:
                batch_no_input = st.text_input("Batch Number *", placeholder="Enter batch Code/Number")

            st.markdown("#### ⚙️ Define Process Sequence (From Operation List)")
            selected_ops = st.multiselect(
                "Select Operations Sequence in Order:",
                options=operation_master,
                default=["Incoming Inspection", "CNC Turning", "Heat Treatment (HT)", "Surface Grinding", "Final Quality Inspection"]
            )

            rc_submitted = st.form_submit_button("Generate & Save Route Card")

            if rc_submitted:
                full_rc_no = f"RC-{rc_number_suffix.strip()}"
                existing_rcs = df_rc["RC No"].astype(str).tolist() if not df_rc.empty else []
                
                if not rc_number_suffix.strip() or not selected_part_no or not batch_no_input.strip() or not rm_qty_input.strip() or not rm_issue_date:
                    st.error("⚠️ Route Card No., Part No., RM Issued Qty, RM Issue Date, and Batch Number are mandatory!")
                elif full_rc_no in existing_rcs:
                    st.error(f"❌ Route Card Number `{full_rc_no}` already exists! Please enter a unique route card number.")
                else:
                    try:
                        parsed_qty = float(rm_qty_input.strip())
                    except ValueError:
                        parsed_qty = 0

                    formatted_indian_date = rm_issue_date.strftime("%d/%m/%Y")

                    import json
                    process_steps = []
                    for idx, op in enumerate(selected_ops, 1):
                        process_steps.append({
                            "process_no": idx,
                            "description": op,
                            "date": "",
                            "qty_received": parsed_qty if idx == 1 else 0,
                            "ok_qty": 0,
                            "rej_qty": 0,
                            "rework_qty": 0,
                            "batch_code": batch_no_input.strip(),
                            "owner_sign": "",
                            "remark": "Pending"
                        })

                    new_rc_row = pd.DataFrame([{
                        "RC No": full_rc_no,
                        "Part No": selected_part_no,
                        "Part Name": part_name_input.strip().upper(),
                        "RM Issue Slip": rm_issue_slip.strip(),
                        "RM Qty": parsed_qty,
                        "RM Issue Date": formatted_indian_date,
                        "Batch No": batch_no_input.strip(),
                        "Process Steps JSON": json.dumps(process_steps),
                        "Status": "Active",
                        "Created Date": time.strftime("%Y-%m-%d %H:%M:%S")
                    }])

                    df_rc = pd.concat([df_rc, new_rc_row], ignore_index=True)
                    df_rc.to_csv(ROUTE_CARDS_FILE, index=False)
                    st.success(f"✅ Route Card `{full_rc_no}` successfully generated for Part `{selected_part_no}`!")
                    st.rerun()

    else:
        st.markdown("### 🔍 Track & Update Route Cards")
        if df_rc.empty:
            st.info("No route cards created yet. Switch to 'Create New Route Card' to generate one.")
        else:
            rc_list = df_rc["RC No"].astype(str).tolist()
            selected_rc = st.selectbox("Select Route Card Number", options=rc_list)
            
            rc_row = df_rc[df_rc["RC No"].astype(str) == selected_rc].iloc[0]
            
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 15px;">
                <b>Route Card No:</b> <code>{rc_row['RC No']}</code> &nbsp;|&nbsp; 
                <b>Part No:</b> <code>{rc_row['Part No']}</code> &nbsp;|&nbsp; 
                <b>Part Name:</b> <code>{rc_row['Part Name']}</code><br>
                <b>Batch No:</b> <code>{rc_row['Batch No']}</code> &nbsp;|&nbsp; 
                <b>RM Qty Issued:</b> <code>{rc_row['RM Qty']}</code> &nbsp;|&nbsp; 
                <b>Issue Date:</b> <code>{rc_row.get('RM Issue Date', 'N/A')}</code> &nbsp;|&nbsp; 
                <b>Slip:</b> <code>{rc_row['RM Issue Slip']}</code>
            </div>
            """, unsafe_allow_html=True)

            import json
            steps = json.loads(rc_row["Process Steps JSON"])
            
            st.markdown("#### 📋 Process Sequence & Shop-Floor Status Log")
            updated_steps = []
            
            for step in steps:
                with st.expander(f"Process #{step['process_no']}: {step['description']} (Status: {step['remark']})"):
                    sc1, sc2, sc3, sc4 = st.columns(4)
                    with sc1:
                        s_date = st.text_input(f"Date [{step['process_no']}]", value=step['date'], key=f"date_{rc_row['RC No']}_{step['process_no']}")
                    with sc2:
                        s_received = st.number_input(f"Qty Received [{step['process_no']}]", value=int(step['qty_received']), key=f"rcv_{rc_row['RC No']}_{step['process_no']}")
                    with sc3:
                        s_ok = st.number_input(f"OK Qty [{step['process_no']}]", value=int(step['ok_qty']), key=f"ok_{rc_row['RC No']}_{step['process_no']}")
                    with sc4:
                        s_rej = st.number_input(f"Rej Qty [{step['process_no']}]", value=int(step['rej_qty']), key=f"rej_{rc_row['RC No']}_{step['process_no']}")

                    sc5, sc6, sc7 = st.columns(3)
                    with sc5:
                        s_rework = st.number_input(f"Rework Qty [{step['process_no']}]", value=int(step['rework_qty']), key=f"rew_{rc_row['RC No']}_{step['process_no']}")
                    with sc6:
                        s_owner = st.text_input(f"Operator / Owner Sign [{step['process_no']}]", value=step['owner_sign'], key=f"own_{rc_row['RC No']}_{step['process_no']}")
                    with sc7:
                        s_remark = st.selectbox(f"Status [{step['process_no']}]", options=["Pending", "In Progress", "Completed", "Hold"], index=["Pending", "In Progress", "Completed", "Hold"].index(step['remark']) if step['remark'] in ["Pending", "In Progress", "Completed", "Hold"] else 0, key=f"rem_{rc_row['RC No']}_{step['process_no']}")

                    updated_steps.append({
                        "process_no": step['process_no'],
                        "description": step['description'],
                        "date": s_date,
                        "qty_received": s_received,
                        "ok_qty": s_ok,
                        "rej_qty": s_rej,
                        "rework_qty": s_rework,
                        "batch_code": rc_row['Batch No'],
                        "owner_sign": s_owner,
                        "remark": s_remark
                    })

            if st.button("💾 Save Process Progress"):
                df_rc.loc[df_rc["RC No"].astype(str) == selected_rc, "Process Steps JSON"] = json.dumps(updated_steps)
                df_rc.to_csv(ROUTE_CARDS_FILE, index=False)
                st.success("✅ Route card progress successfully updated!")
                st.rerun()

            if role_val == "Admin":
                if st.button("🗑️ Delete Route Card"):
                    df_rc = df_rc[df_rc["RC No"].astype(str) != selected_rc]
                    df_rc.to_csv(ROUTE_CARDS_FILE, index=False)
                    st.warning(f"Route card `{selected_rc}` deleted.")
                    st.rerun()


# ================= VIEW 4: DOCUMENTATION =================
elif nav_selection == "📋 Documentation":
    st.subheader("📋 Quality & Engineering Documentation")
    
    DOC_FILE = "documentation.json"
    
    default_docs = {
        "Control Plan": "# Control Plan\n\n- **Process Name:** Gear Manufacturing\n- **Stage:** Machining & Heat Treatment\n- **Parameters:** Dimensions, Hardness, Surface Finish.",
        "PFMEA": "# Process Failure Mode and Effects Analysis (PFMEA)\n\n- **System:** Kinetic Gears Production\n- **Potential Failure Mode:** Out of tolerance bore diameter.\n- **Severity/Occ/Det:** 8 / 3 / 4",
        "Process Flow Diagram (PFD)": "# Process Flow Diagram (PFD)\n\n1. Raw Material Inspection (Forging/Bar)\n2. CNC Turning / Hobbing\n3. Heat Treatment\n4. Grinding & Finishing\n5. Final Quality Inspection",
        "Checksheets": "# Quality Checksheets\n\n- Daily calibration check for Mitutoyo Surftest SJ-210.\n- Visual inspection checklist for surface defects and burrs."
    }
    
    if os.path.exists(DOC_FILE):
        try:
            with open(DOC_FILE, "r") as f:
                docs_data = json.load(f)
        except Exception:
            docs_data = default_docs
    else:
        docs_data = default_docs
        with open(DOC_FILE, "w") as f:
            json.dump(default_docs, f, indent=4)

    doc_categories = list(docs_data.keys())
    selected_doc = st.selectbox("Select Quality Document", doc_categories, key="doc_selector")

    st.markdown("---")

    if role_val == "Admin":
        with st.form("doc_edit_form"):
            st.markdown(f"**Editing Mode: `{selected_doc}`** (Admin privilege active)")
            edited_content = st.text_area("Document Content (Markdown supported)", value=docs_data.get(selected_doc, ""), height=350)
            doc_submitted = st.form_submit_button("Save Document Changes")

            if doc_submitted:
                docs_data[selected_doc] = edited_content
                with open(DOC_FILE, "w") as f:
                    json.dump(docs_data, f, indent=4)
                st.success(f"Successfully updated `{selected_doc}`!")
                st.rerun()
    else:
        st.markdown(f"### 📖 Viewing: {selected_doc}")
        st.markdown(
            f"""
            <div style="background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.1); color: #ffffff;">
                {docs_data.get(selected_doc, 'No content available.')}
            </div>
            """,
            unsafe_allow_html=True
        )
        st.info("🔒 Document editing is restricted to Administrator accounts only.")
