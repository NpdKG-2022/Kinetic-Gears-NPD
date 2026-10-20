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

# Custom CSS for Glassmorphism login, layouts, Enterprise Styled Tabs, and Hover-Expanding Logout Button
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
    if "Item Code" in df_drawings.columns and "CODE NO." not in df_drawings.columns:
        df_drawings = df_drawings.rename(columns={"Item Code": "CODE NO."})
    if "Drawing File" in df_drawings.columns and "Drawing" not in df_drawings.columns:
        df_drawings = df_drawings.rename(columns={"Drawing File": "Drawing"})
        
    if not df_drawings.empty and not df_tracker.empty and "CODE NO." in df_tracker.columns and "CODE NO." in df_drawings.columns:
        df_tracker = pd.merge(df_tracker, df_drawings, on="CODE NO.", how="left", suffixes=("", "_map"))
        if "Drawing_map" in df_tracker.columns:
            df_tracker["Drawing"] = df_tracker["Drawing_map"].combine_first(
                df_tracker.get("Drawing", pd.Series([None] * len(df_tracker)))
            )
            df_tracker = df_tracker.drop(columns=[c for c in df_tracker.columns if "_map" in c])

if "Drawing" not in df_tracker.columns:
    df_tracker["Drawing"] = ""

# ================= ENTERPRISE STYLED TABS =================
tab1, tab2, tab3 = st.tabs(["🔍 View Drawing (In-Browser)", "📐 Manage Drawings", "📋 Documentation"])


# ================= TAB 1: VIEW DRAWING =================
with tab1:
    st.subheader("🔍 In-Browser Engineering Drawing Viewer")
    
    # Restrict search bar row to 3/4th width of the page
    main_search_col, _ = st.columns([3, 1])

    with main_search_col:
        r_col1, r_col2, r_col3 = st.columns([1.5, 1.5, 3])

        with r_col1:
            st.markdown("<p style='font-size: 14px; font-weight: 600; padding-top: 8px; margin-bottom: 0;'>Search Drawing By:</p>", unsafe_allow_html=True)

        with r_col2:
            search_mode = st.radio("Search Mode", ["Part No.", "Part Name"], horizontal=True, label_visibility="collapsed")

        with r_col3:
            target_col = "CODE NO." if search_mode == "Part No." else "ITEM NAME"
            all_options = sorted(df_tracker[target_col].astype(str).unique().tolist()) if not df_tracker.empty and target_col in df_tracker.columns else []
            
            # Google-style searchable dropdown autocomplete acting as live search bar with suggestions
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
        c_code = row.get("CODE NO.", "")
        c_item = row.get("ITEM NAME", "")
        drawing_path = row.get("Drawing", "")

        st.markdown("---")
        st.info(f"**Part No:** `{c_code}` | **Part Name:** `{c_item}`")

       if pd.notna(drawing_path) and str(drawing_path).strip() != "" and os.path.exists(str(drawing_path)):
            st.success("Drawing loaded successfully in viewer:")
            if drawing_path.lower().endswith((".png", ".jpg", ".jpeg", ".tiff", ".tif", ".svg")):
                st.image(drawing_path, caption=f"Drawing: {c_code} - {c_item}", use_column_width=True)
            elif drawing_path.lower().endswith(".pdf"):
                try:
                    from streamlit_pdf_viewer import pdf_viewer
                    pdf_viewer(drawing_path, width=700, height=700)
                except ImportError:
                    # Fallback if package isn't installed
                    with open(drawing_path, "rb") as f:
                        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
                    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="700px" type="application/pdf"></iframe>'
                    st.markdown(pdf_display, unsafe_allow_html=True)
                
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
        st.info(f"Type or select a {search_mode} above to instantly view your drawing")


# ================= TAB 2: MANAGE DRAWINGS =================
with tab2:
    st.subheader("📐 Add or Update Drawings with Part Details")
    
    with st.form("drawing_manager_form"):
        # Part Number and Part Name side-by-side in one line
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            manual_code = st.text_input("Enter Part Number *", placeholder="e.g. PM-001")
        with col_p2:
            manual_item_name = st.text_input("Enter Part Name *", placeholder="e.g. Gear Blank")

        # File uploader constrained to 1/3rd width of the page using columns ([1, 2])
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

                # 1. Update/Save drawing map file safely
                if os.path.exists(DRAWINGS_MAP_FILE):
                    df_d_map = pd.read_csv(DRAWINGS_MAP_FILE)
                    if "Item Code" in df_d_map.columns and "CODE NO." not in df_d_map.columns:
                        df_d_map = df_d_map.rename(columns={"Item Code": "CODE NO."})
                    if "Drawing File" in df_d_map.columns and "Drawing" not in df_d_map.columns:
                        df_d_map = df_d_map.rename(columns={"Drawing File": "Drawing"})
                else:
                    df_d_map = pd.DataFrame(columns=["CODE NO.", "Drawing"])

                if "CODE NO." in df_d_map.columns:
                    df_d_map = df_d_map[df_d_map["CODE NO."].astype(str) != str(manual_code.strip())]
                
                updated_map = pd.concat([df_d_map, pd.DataFrame({"CODE NO.": [manual_code.strip()], "Drawing": [file_save_path]})], ignore_index=True)
                updated_map.to_csv(DRAWINGS_MAP_FILE, index=False)

                # 2. Update/Save custom items tracker dataframe
                if os.path.exists(CUSTOM_ITEMS_FILE):
                    df_custom = pd.read_csv(CUSTOM_ITEMS_FILE)
                else:
                    df_custom = pd.DataFrame(columns=["Plant", "CODE NO.", "ITEM NAME", "PRICE", "Drawing"] + months_list)

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


# ================= TAB 3: DOCUMENTATION =================
with tab3:
    st.subheader("📋 Quality & Engineering Documentation")
    
    DOC_FILE = "documentation.json"
    
    default_docs = {
        "Control Plan": "# Control Plan\n\n- **Process Name:** Gear Manufacturing\n- **Stage:** Machining & Heat Treatment\n- **Parameters:** Dimensions, Hardness, Surface Finish.",
        "PFMEA": "# Process Failure Mode and Effects Analysis (PFMEA)\n\n- **System:** Kinetic Gears Production\n- **Potential Failure Mode:** Out of tolerance bore diameter.\n- **Severity/Occ/Det:** 8 / 3 / 4",
        "Process Flow Diagram (PFD)": "# Process Flow Diagram (PFD)\n\n1. Raw Material Inspection (Forging/Bar)\n2. CNC Turning / Hobbing\n3. Heat Treatment\n4. Grinding & Finishing\n5. Final Quality Inspection",
        "Checksheets": "# Quality Checksheets\n\n- Daily calibration check for Mitutoyo Surftest SJ-210.\n- Visual inspection checklist for surface defects and burrs."
    }
    
    # Load or initialize documentation store
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

    # Document selection
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
