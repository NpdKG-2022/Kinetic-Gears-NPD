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

# ================= NAVIGATION MENU & TABS =================
st.markdown("📌 **Navigation Menu**")
selected_tab = st.radio(
    "Navigation",
    [
        "📊 Dashboard & Tracking",
        "🔍 View Drawing (In-Browser)",
        "📝 Enter Dispatches",
        "📐 Manage Drawings",
        "➕ Add New Item Schedule"
    ],
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("---")

# Setup default dataframes and directories
os.makedirs("drawings", exist_ok=True)
DRAWINGS_DIR = "drawings"
DRAWINGS_MAP_FILE = "item_drawings.csv"
LOG_FILE = "dispatch_logs.csv"
CUSTOM_ITEMS_FILE = "custom_items.csv"
months_list = ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]

# Load base tracker dataframe
if os.path.exists(CUSTOM_ITEMS_FILE):
    df_tracker = pd.read_csv(CUSTOM_ITEMS_FILE)
else:
    df_tracker = pd.DataFrame(columns=["Plant", "CODE NO.", "ITEM NAME", "PRICE", "Drawing"] + months_list)

if os.path.exists(LOG_FILE):
    log_df = pd.read_csv(LOG_FILE)
else:
    log_df = pd.DataFrame(columns=["Date", "Plant", "CODE NO.", "ITEM NAME", "Month", "Dispatched Qty", "Logged By"])


# ================= TAB 1: DASHBOARD & TRACKING =================
if selected_tab == "📊 Dashboard & Tracking":
    st.subheader("📊 Dashboard & Item Tracking")
    if not df_tracker.empty:
        st.dataframe(df_tracker, use_container_width=True, hide_index=True)
    else:
        st.info("No item schedules available yet. Use 'Add New Item Schedule' tab to add items.")


# ================= TAB 2: VIEW DRAWING (IN-BROWSER) =================
elif selected_tab == "🔍 View Drawing (In-Browser)":
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

    target_file = None
    c_code, c_item, c_plant = "", "", ""

    if not matched_rows.empty:
        row = matched_rows.iloc[0]
        c_code = row.get("CODE NO.", "")
        c_item = row.get("ITEM NAME", "")
        c_plant = row.get("Plant", "")
        target_file = row.get("Drawing", "")

    # Fallback to drawings folder if mapping CSV drawing path is empty
    drawing_files = [f for f in os.listdir(DRAWINGS_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf', '.webp', '.svg'))] if os.path.exists(DRAWINGS_DIR) else []
    if not target_file or pd.isna(target_file) or not os.path.exists(str(target_file)):
        if drawing_files:
            target_file = drawing_files[0]

    st.markdown("---")
    view_col1, view_col2 = st.columns([1, 2])

    with view_col1:
        st.markdown("#### Item Specifications")
        if not matched_rows.empty:
            st.info(f"**Plant:** {c_plant}\n\n**Code No:** `{c_code}`\n\n**Item Name:** `{c_item}`")
        else:
            st.info("Select an item above to view specifications.")
            
        if drawing_files:
            sel_file = st.selectbox("Or Browse Available Drawings:", drawing_files)
            if sel_file:
                target_file = os.path.join(DRAWINGS_DIR, sel_file)

    with view_col2:
        st.markdown("#### Drawing Preview & Specifications")
        if target_file and os.path.exists(str(target_file)):
            file_path = str(target_file)
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.svg')):
                st.image(file_path, caption=f"Drawing: {target_file}", use_column_width=True)
            elif file_path.lower().endswith('.pdf'):
                st.success(f"PDF Drawing loaded: {os.path.basename(file_path)}")
                with open(file_path, "rb") as pdf_file:
                    base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
                
                pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600px" type="application/pdf">'
                st.markdown(pdf_display, unsafe_allow_html=True)
                
                # Admin-only download button restriction
                if role_val == "Admin":
                    st.markdown("<br>", unsafe_allow_html=True)
                    with open(file_path, "rb") as pdf_file:
                        PDFbyte = pdf_file.read()
                    st.download_button(label="📥 Download Drawing PDF", data=PDFbyte, file_name=os.path.basename(file_path), mime='application/pdf')
                else:
                    st.info("🔒 Download restricted to Administrator accounts only.")
        else:
            st.info("Please select a Code No. or Item Name above to view its drawing.")


# ================= TAB 3: ENTER DISPATCHES =================
elif selected_tab == "📝 Enter Dispatches":
    st.subheader("📝 Record Monthly Dispatch")
    if "d_qty" not in st.session_state:
        st.session_state["d_qty"] = 0

    if not df_tracker.empty and "Plant" in df_tracker.columns:
        with st.form("dispatch_entry_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                form_plant = st.selectbox("Plant Name", options=df_tracker["Plant"].dropna().unique(), key="d_plant")

            plant_items = df_tracker[df_tracker["Plant"] == form_plant]
            item_options_dict = dict(zip(plant_items["ITEM NAME"], plant_items["CODE NO."]))

            with col2:
                form_item = st.selectbox("Item Name", options=list(item_options_dict.keys()), key="d_item")
                form_code = item_options_dict.get(form_item, "")

            with col3:
                form_month = st.selectbox("Target Month", options=months_list, key="d_month")

            dispatch_qty = st.number_input("Dispatched Quantity", min_value=0, step=1, key="d_qty")
            submitted = st.form_submit_button("Save Dispatch Entry")

            if submitted:
                new_entry = pd.DataFrame({
                    "Date": [pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")],
                    "Plant": [form_plant],
                    "CODE NO.": [form_code],
                    "ITEM NAME": [form_item],
                    "Month": [form_month],
                    "Dispatched Qty": [dispatch_qty],
                    "Logged By": [st.session_state["username"]],
                })
                new_entry.to_csv(LOG_FILE, mode="a", header=not os.path.exists(LOG_FILE), index=False)
                st.success(f"Successfully recorded {dispatch_qty} units for {form_item} ({form_plant}) in {form_month}!")
                st.session_state["d_qty"] = 0
                st.rerun()
    else:
        st.warning("No plant schedules found. Please add item schedules first.")

    st.markdown("---")
    st.subheader("📋 Raw Dispatch Entry History")
    if not log_df.empty:
        st.dataframe(log_df, use_container_width=True, hide_index=True)
        if st.session_state["role"] == "Admin":
            if st.button("🗑️ Clear All Dispatch Logs"):
                if os.path.exists(LOG_FILE):
                    os.remove(LOG_FILE)
                st.success("Dispatch log history cleared!")
                st.rerun()
    else:
        st.info("No dispatch entries logged yet.")


# ================= TAB 4: MANAGE DRAWINGS =================
elif selected_tab == "📐 Manage Drawings":
    st.subheader("📐 Attach or Update Drawings for Code Numbers")
    if not df_tracker.empty and "CODE NO." in df_tracker.columns:
        all_unique_codes = sorted(df_tracker["CODE NO."].astype(str).unique().tolist())

        with st.form("drawing_manager_form"):
            selected_code_for_drawing = st.selectbox("Select Code No.", options=all_unique_codes)
            match_row = df_tracker[df_tracker["CODE NO."].astype(str) == selected_code_for_drawing]
            if not match_row.empty:
                st.markdown(f"**Associated Item Name:** `{match_row.iloc[0]['ITEM NAME']}`")

            uploaded_file = st.file_uploader("Upload Drawing File (PDF, PNG, JPG)", type=["pdf", "png", "jpg", "jpeg", "webp"])
            drawing_submitted = st.form_submit_button("Save Drawing Link")

            if drawing_submitted:
                if uploaded_file is not None:
                    file_save_path = os.path.join(DRAWINGS_DIR, uploaded_file.name)
                    with open(file_save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    df_d_map = pd.read_csv(DRAWINGS_MAP_FILE) if os.path.exists(DRAWINGS_MAP_FILE) else pd.DataFrame(columns=["CODE NO.", "Drawing"])
                    df_d_map = df_d_map[df_d_map["CODE NO."].astype(str) != str(selected_code_for_drawing)]
                    
                    updated_map = pd.concat([df_d_map, pd.DataFrame({"CODE NO.": [selected_code_for_drawing], "Drawing": [file_save_path]})], ignore_index=True)
                    updated_map.to_csv(DRAWINGS_MAP_FILE, index=False)

                    # Update main tracker/custom items drawing column if present
                    if "Drawing" in df_tracker.columns:
                        df_tracker.loc[df_tracker["CODE NO."].astype(str) == str(selected_code_for_drawing), "Drawing"] = file_save_path
                        df_tracker.to_csv(CUSTOM_ITEMS_FILE, index=False)

                    st.success(f"Successfully linked drawing to Code No: {selected_code_for_drawing}!")
                    st.rerun()
                else:
                    st.error("Please upload a drawing file first.")
    else:
        st.info("No items found to manage drawings for.")


# ================= TAB 5: ADD NEW ITEM SCHEDULE =================
elif selected_tab == "➕ Add New Item Schedule":
    st.subheader("➕ Add New Item & Plant Requirement Schedule")
    with st.form("new_item_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            new_plant = st.text_input("Plant Name (e.g. KMC-AT)")
        with c2:
            new_code = st.text_input("Code No. (e.g. 1109999-00)")
        with c3:
            new_item_name = st.text_input("Item Name / Description")

        c4, _ = st.columns(2)
        with c4:
            new_price = st.number_input("Unit Price", min_value=0.0, value=1.0, step=0.01)

        st.markdown("##### Monthly Firm Schedules (Apr – Mar)")
        m_cols = st.columns(6)
        new_schedules = {}
        for i, m in enumerate(months_list):
            with m_cols[i % 6]:
                new_schedules[m] = st.number_input(m, min_value=0, value=0, step=1, key=f"sch_{m}")

        uploaded_drawing = st.file_uploader("Choose a drawing file", type=["pdf", "png", "jpg", "jpeg", "webp"], key="new_item_drawing")
        add_submitted = st.form_submit_button("Save New Item")

        if add_submitted:
            if not new_plant or not new_code or not new_item_name:
                st.error("Please fill in Plant, Code No., and Item Name.")
            else:
                drawing_saved_path = ""
                if uploaded_drawing is not None:
                    drawing_saved_path = os.path.join(DRAWINGS_DIR, uploaded_drawing.name)
                    with open(drawing_saved_path, "wb") as f:
                        f.write(uploaded_drawing.getbuffer())

                row_data = {
                    "Plant": [new_plant],
                    "CODE NO.": [new_code],
                    "ITEM NAME": [new_item_name.upper()],
                    "PRICE": [new_price],
                    "Drawing": [drawing_saved_path],
                }
                for m in months_list:
                    row_data[m] = [new_schedules[m]]

                df_new_row = pd.DataFrame(row_data)
                if os.path.exists(CUSTOM_ITEMS_FILE):
                    df_new_row.to_csv(CUSTOM_ITEMS_FILE, mode="a", header=False, index=False)
                else:
                    df_new_row.to_csv(CUSTOM_ITEMS_FILE, index=False)

                st.success(f"Successfully added new item '{new_item_name}' (Code: {new_code}) for plant {new_plant}!")
                st.rerun()
