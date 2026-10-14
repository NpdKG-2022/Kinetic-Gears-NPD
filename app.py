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
    layout="wide"
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

# Select a random wallpaper for this session load
selected_wallpaper = random.choice(manufacturing_wallpapers)

# Custom CSS for Glassmorphism login and navigation cards
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
        
        /* Transform dashboard buttons into interactive navigation cards */
        div[data-testid="column"] button {{
            border-radius: 24px !important;
            padding: 20px 10px !important;
            height: 120px !important;
            width: 100% !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
            transition: all 0.3s ease !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            white-space: pre-wrap !important;
        }}
        div[data-testid="column"] button:hover {{
            transform: translateY(-5px) !important;
            box-shadow: 0 8px 25px rgba(0,0,0,0.3) !important;
        }}

        /* Individual Card Colors & Borders based on Column Position */
        div[data-testid="column"]:nth-child(1) button {{
            background-color: #ffebee !important;
            color: #c2185b !important;
            border: 2px solid #c2185b !important;
        }}
        div[data-testid="column"]:nth-child(2) button {{
            background-color: #e0f7fa !important;
            color: #00838f !important;
            border: 2px solid #00838f !important;
        }}
        div[data-testid="column"]:nth-child(3) button {{
            background-color: #f3e5f5 !important;
            color: #7b1fa2 !important;
            border: 2px solid #7b1fa2 !important;
        }}
        div[data-testid="column"]:nth-child(4) button {{
            background-color: #e8f5e9 !important;
            color: #2e7d32 !important;
            border: 2px solid #2e7d32 !important;
        }}
        div[data-testid="column"]:nth-child(5) button {{
            background-color: #fff3e0 !important;
            color: #ef6c00 !important;
            border: 2px solid #ef6c00 !important;
        }}
    </style>
""",
    unsafe_allow_html=True,
)

# ================= USER AUTHENTICATION & PERSISTENCE SETUP =================
USERS = {
    "admin": {"password": "admin123", "role": "Admin"},
    "operator1": {"password": "password1", "role": "Operator"},
    "manager": {"password": "manager123", "role": "Manager"},
}

SESSION_TIMEOUT = 600  # 10 minutes in seconds

# Synchronize session state with query parameters for refresh survival
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

# Initialize navigation tab state if not present
if "selected_tab" not in st.session_state:
    st.session_state["selected_tab"] = "📊 Dashboard & Tracking"


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


# ================= SESSION TIMEOUT CHECK =================
if st.session_state["logged_in"]:
    elapsed = time.time() - st.session_state.get("login_time", time.time())
    if elapsed > SESSION_TIMEOUT:
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.session_state["role"] = ""
        st.session_state["login_time"] = 0.0
        st.query_params.clear()
        st.warning(
            "⏱ Your session has expired due to 10 minutes of inactivity. Please"
            " log in again."
        )
        st.rerun()

if not st.session_state["logged_in"]:
    login_screen()
    st.stop()

# ================= TOP PAGE TITLE =================
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 0px;">
        <h1 style="font-size: 50px; margin-bottom: 0px; color: white;">🏭 CENTURY DESIGNS Tracking System</h1>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("---")

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
            body {
                margin: 0;
                background-color: transparent;
            }
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
                
                document.getElementById('futuristic-time').innerText = `${formattedHours}:${minutes}:${seconds} ${ampm}`;
                
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
    elapsed = time.time() - st.session_state.get("login_time", time.time())
    remaining_secs = max(0, int(SESSION_TIMEOUT - elapsed))
    mins, secs = divmod(remaining_secs, 60)
    st.markdown(f"<div style='color: white;'>⏳ Expires:<br><b>{mins:02d}:{secs:02d}</b></div>", unsafe_allow_html=True)

with top_c4:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.session_state["role"] = ""
        st.session_state["login_time"] = 0.0
        st.query_params.clear()
        st.rerun()

st.markdown("---")

EXCEL_FILE = "Book1.xlsx"
LOG_FILE = "dispatch_log.csv"
CUSTOM_ITEMS_FILE = "custom_items.csv"
DRAWINGS_MAP_FILE = "item_drawings.csv"
DRAWINGS_DIR = "drawings"

os.makedirs(DRAWINGS_DIR, exist_ok=True)

months_list = [
    "Apr", "May", "Jun", "Jul", "Aug", "Sep",
    "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"
]


@st.cache_data
def load_schedule_data():
    if not os.path.exists(EXCEL_FILE):
        return None
    df_raw = pd.read_excel(EXCEL_FILE, sheet_name="KMC TOTAL")
    df = df_raw.iloc[1:].copy()
    df = df.dropna(subset=["Plant", "CODE NO."])

    for m in months_list:
        df[m] = pd.to_numeric(df[m], errors="coerce").fillna(0)

    df["PRICE"] = pd.to_numeric(df["PRICE"], errors="coerce").fillna(0.0)

    if os.path.exists(CUSTOM_ITEMS_FILE):
        df_custom = pd.read_csv(CUSTOM_ITEMS_FILE)
        if not df_custom.empty:
            for m in months_list:
                if m in df_custom.columns:
                    df_custom[m] = pd.to_numeric(df_custom[m], errors="coerce").fillna(0)
            df = pd.concat([df, df_custom], ignore_index=True)

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


df_schedule = load_schedule_data()

if df_schedule is None:
    st.error(
        f"Could not find '{EXCEL_FILE}' in the directory. Please place it in the folder."
    )
else:
    if not os.path.exists(LOG_FILE):
        pd.DataFrame(
            columns=[
                "Date", "Plant", "CODE NO.", "ITEM NAME",
                "Month", "Dispatched Qty", "Logged By"
            ]
        ).to_csv(LOG_FILE, index=False)

    log_df = pd.read_csv(LOG_FILE)

    if not log_df.empty and "Dispatched Qty" in log_df.columns:
        disp_summary = (
            log_df.groupby(["Plant", "CODE NO."])["Dispatched Qty"]
            .sum()
            .reset_index()
            .rename(columns={"Dispatched Qty": "Disp. Till date"})
        )
    else:
        disp_summary = pd.DataFrame(
            columns=["Plant", "CODE NO.", "Disp. Till date"]
        )

    df_tracker = pd.merge(
        df_schedule, disp_summary, on=["Plant", "CODE NO."], how="left"
    )
    df_tracker["Disp. Till date"] = (
        df_tracker["Disp. Till date"].fillna(0).astype(int)
    )
    df_tracker["Balance"] = (
        df_tracker["Total_Schedule"] - df_tracker["Disp. Till date"]
    )

    # ================= CARD GRID NAVIGATION MENU =================
    st.markdown("<h3 style='color: white;'>📌 Navigation Menu</h3>", unsafe_allow_html=True)

    tabs_config = [
        {"title": "Dashboard & Tracking", "icon": "📊", "bg": "#ffebee", "color": "#c2185b"},
        {"title": "View Drawing (In-Browser)", "icon": "🔍", "bg": "#e0f7fa", "color": "#00838f"},
        {"title": "Enter Dispatches", "icon": "📝", "bg": "#f3e5f5", "color": "#7b1fa2"},
        {"title": "Manage Drawings", "icon": "📐", "bg": "#e8f5e9", "color": "#2e7d32"},
        {"title": "Add New Item Schedule", "icon": "➕", "bg": "#fff3e0", "color": "#ef6c00"}
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

    # ================= TAB 1: DASHBOARD =================
    if selected_tab == "📊 Dashboard & Tracking":
        st.markdown("<h3 style='color: white;'>📊 Live Tracking Summary</h3>", unsafe_allow_html=True)
        st.markdown(
            "<span style='color: rgba(255,255,255,0.7);'>(Note: Monthly columns are color-coded: 🟩 Green = Complete, 🟨 Yellow = Partial)</span>",
            unsafe_allow_html=True
        )

        f_col1, f_col2, f_col3 = st.columns(3)
        plants = ["All"] + list(df_tracker["Plant"].dropna().unique())
        with f_col1:
            selected_plant = st.selectbox("Select Plant", options=plants, key="dash_plant")

        filtered_by_plant = (
            df_tracker
            if selected_plant == "All"
            else df_tracker[df_tracker["Plant"] == selected_plant]
        )

        code_options = ["All"] + sorted(
            filtered_by_plant["CODE NO."].astype(str).unique().tolist()
        )
        with f_col2:
            selected_code = st.selectbox("Select Code No.", options=code_options, key="dash_code")

        item_options = ["All"] + sorted(
            filtered_by_plant["ITEM NAME"].astype(str).unique().tolist()
        )
        with f_col3:
            selected_item = st.selectbox("Select Item Name", options=item_options, key="dash_item")

        view_df = filtered_by_plant.copy()
        if selected_code != "All":
            view_df = view_df[view_df["CODE NO."].astype(str) == selected_code]
        if selected_item != "All":
            view_df = view_df[view_df["ITEM NAME"].astype(str) == selected_item]

        def highlight_schedule_completion(row):
            styles = [""] * len(row)
            total_disp = float(row.get("Disp. Till date", 0))
            remaining_disp = total_disp

            for i, col_name in enumerate(row.index):
                if col_name in months_list:
                    try:
                        sched_val = float(row[col_name])
                    except ValueError:
                        sched_val = 0.0

                    if sched_val > 0:
                        if remaining_disp >= sched_val:
                            styles[i] = "background-color: rgba(102, 255, 0, 1.0); color: black;"
                            remaining_disp -= sched_val
                        elif remaining_disp > 0:
                            styles[i] = "background-color: rgba(241, 196, 15, 0.6); color: black;"
                            remaining_disp = 0
            return styles

        display_table_df = view_df.drop(columns=["Drawing"], errors="ignore")
        st.markdown("---")

        numeric_cols = months_list + ["Total_Schedule", "Disp. Till date", "Balance"]
        format_dict = {}
        for col in display_table_df.columns:
            if col in numeric_cols or col == "PRICE":
                format_dict[col] = (
                    lambda val: f"{int(val)}"
                    if pd.notna(val) and float(val).is_integer()
                    else f"{val}"
                )

        styled_df = (
            display_table_df.style.apply(highlight_schedule_completion, axis=1)
            .format(format_dict, na_rep="")
        )
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

        # ================= EXPORT OPTIONS =================
        st.markdown("<h3 style='color: white;'>📥 Export Tracking Data</h3>", unsafe_allow_html=True)
        e_col1, e_col2 = st.columns([1, 2])

        with e_col1:
            export_format = st.selectbox(
                "Choose Export Format", options=[".xlsx", ".xls", ".pdf"], key="exp_fmt"
            )

        with e_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if export_format in [".xlsx", ".xls"]:
                output = io.BytesIO()
                engine = "openpyxl" if export_format == ".xlsx" else "xlwt"
                try:
                    with pd.ExcelWriter(output, engine=engine) as writer:
                        current_timestamp = pd.Timestamp.now().strftime("%A, %Y-%m-%d %H:%M:%S")
                        current_user = st.session_state.get("username", "Unknown")

                        metadata_df = pd.DataFrame([
                            ["Century Designs - Plant Dispatch Tracking Report"],
                            [f"Generated on: {current_timestamp}"],
                            [f"Exported by User: {current_user}"],
                            [""]
                        ])
                        metadata_df.to_excel(writer, index=False, header=False, sheet_name="Tracking")
                        display_table_df.to_excel(writer, index=False, startrow=4, sheet_name="Tracking")

                    excel_data = output.getvalue()
                    st.download_button(
                        label=f"Download File ({export_format})",
                        data=excel_data,
                        file_name=f"dispatch_tracker{export_format}",
                        mime=(
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            if export_format == ".xlsx"
                            else "application/vnd.ms-excel"
                        ),
                        use_container_width=True,
                    )
                except Exception as ex:
                    st.error(f"Error generating Excel file: {ex}")

            elif export_format == ".pdf":
                from reportlab.lib import colors
                from reportlab.lib.pagesizes import A4, landscape
                from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

                pdf_buffer = io.BytesIO()
                doc = SimpleDocTemplate(
                    pdf_buffer,
                    pagesize=landscape(A4),
                    rightMargin=20,
                    leftMargin=20,
                    topMargin=20,
                    bottomMargin=20,
                )
                story = []
                styles = getSampleStyleSheet()

                title_style = ParagraphStyle(
                    "TitleStyle",
                    parent=styles["Heading1"],
                    fontSize=16,
                    textColor=colors.HexColor("#1f4e78"),
                    spaceAfter=4,
                )

                meta_style = ParagraphStyle(
                    "MetaStyle",
                    parent=styles["Normal"],
                    fontSize=9,
                    textColor=colors.HexColor("#555555"),
                    spaceAfter=12,
                )

                story.append(
                    Paragraph("Century Designs - Plant Dispatch Tracking Report", title_style)
                )

                current_timestamp = pd.Timestamp.now().strftime("%A, %B %d, %Y - %H:%M:%S")
                current_user = st.session_state.get("username", "Unknown")

                meta_text = f"<b>Generated on:</b> {current_timestamp} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Exported by:</b> {current_user}"
                story.append(Paragraph(meta_text, meta_style))

                headers = list(display_table_df.columns)
                table_data = [headers]
                for _, row in display_table_df.iterrows():
                    table_data.append([str(row[col]) if pd.notna(row[col]) else "" for col in headers])

                t = Table(table_data)
                t.setStyle(
                    TableStyle([
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e78")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f9f9f9")),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d3d3d3")),
                        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 1), (-1, -1), 7),
                    ])
                )
                story.append(t)
                doc.build(story)
                pdf_data = pdf_buffer.getvalue()

                st.download_button(
                    label="Download File (.pdf)",
                    data=pdf_data,
                    file_name="dispatch_tracker.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

    # ================= TAB 2: VIEW DRAWING =================
    elif selected_tab == "🔍 View Drawing (In-Browser)":
        st.markdown("<h3 style='color: white;'>🔍 In-Browser Engineering Drawing Viewer</h3>", unsafe_allow_html=True)
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

    # ================= TAB 3: ENTER DISPATCHES =================
    elif selected_tab == "📝 Enter Dispatches":
        st.markdown("<h3 style='color: white;'>📝 Record Monthly Dispatch</h3>", unsafe_allow_html=True)

        if "d_qty" not in st.session_state:
            st.session_state["d_qty"] = 0

        with st.form("dispatch_entry_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                form_plant = st.selectbox(
                    "Plant Name",
                    options=df_tracker["Plant"].dropna().unique(),
                    key="d_plant",
                )

            plant_items = df_tracker[df_tracker["Plant"] == form_plant]
            item_options_dict = dict(
                zip(plant_items["ITEM NAME"], plant_items["CODE NO."])
            )

            with col2:
                form_item = st.selectbox(
                    "Item Name", options=list(item_options_dict.keys()), key="d_item"
                )
                form_code = item_options_dict.get(form_item, "")

            with col3:
                form_month = st.selectbox(
                    "Target Month", options=months_list, key="d_month"
                )

            dispatch_qty = st.number_input(
                "Dispatched Quantity", min_value=0, step=1, key="d_qty"
            )
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
                new_entry.to_csv(LOG_FILE, mode="a", header=False, index=False)
                st.success(
                    f"Successfully recorded {dispatch_qty} units for {form_item} "
                    f"({form_plant}) in {form_month}!"
                )
                st.session_state["d_qty"] = 0
                st.rerun()

        st.markdown("---")
        st.markdown("<h3 style='color: white;'>📋 Raw Dispatch Entry History</h3>", unsafe_allow_html=True)
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
        st.markdown("<h3 style='color: white;'>📐 Attach or Update Drawings for Code Numbers</h3>", unsafe_allow_html=True)
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

    # ================= TAB 5: ADD NEW ITEM SCHEDULE =================
    elif selected_tab == "➕ Add New Item Schedule":
        st.markdown("<h3 style='color: white;'>➕ Add New Item & Plant Requirement Schedule</h3>", unsafe_allow_html=True)
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
                new_price = st.number_input(
                    "Unit Price", min_value=0.0, value=1.0, step=0.01
                )

            st.markdown("##### Monthly Firm Schedules (Apr – Mar)")
            m_cols = st.columns(6)
            new_schedules = {}
            for i, m in enumerate(months_list):
                with m_cols[i % 6]:
                    new_schedules[m] = st.number_input(
                        m, min_value=0, value=0, step=1, key=f"sch_{m}"
                    )

            uploaded_drawing = st.file_uploader(
                "Choose a drawing file",
                type=["pdf", "png", "jpg", "jpeg"],
                key="new_item_drawing",
            )
            add_submitted = st.form_submit_button("Save New Item")

            if add_submitted:
                if not new_plant or not new_code or not new_item_name:
                    st.error("Please fill in Plant, Code No., and Item Name.")
                else:
                    drawing_saved_path = ""
                    if uploaded_drawing is not None:
                        drawing_saved_path = os.path.join(
                            DRAWINGS_DIR, uploaded_drawing.name
                        )
                        with open(drawing_saved_path, "wb") as f:
                            f.write(uploaded_drawing.getbuffer())

                        df_d_map = (
                            pd.read_csv(DRAWINGS_MAP_FILE)
                            if os.path.exists(DRAWINGS_MAP_FILE)
                            else pd.DataFrame(columns=["CODE NO.", "Drawing"])
                        )
                        df_d_map = df_d_map[
                            df_d_map["CODE NO."].astype(str) != str(new_code)
                        ]
                        pd.concat(
                            [
                                df_d_map,
                                pd.DataFrame({
                                    "CODE NO.": [new_code],
                                    "Drawing": [drawing_saved_path],
                                }),
                            ],
                            ignore_index=True,
                        ).to_csv(DRAWINGS_MAP_FILE, index=False)

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
                        df_new_row.to_csv(
                            CUSTOM_ITEMS_FILE, mode="a", header=False, index=False
                        )
                    else:
                        df_new_row.to_csv(CUSTOM_ITEMS_FILE, index=False)

                    st.success(
                        f"Successfully added new item '{new_item_name}' (Code: {new_code}) for plant {new_plant}!"
                    )
                    st.rerun()
