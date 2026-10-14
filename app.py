import base64
import io
import os
import time
import pandas as pd
import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="Kinetic Gears",
    page_icon="KG-Logo.png",
    layout="wide",
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
# Custom CSS for clean autofit table display and card button styling
st.markdown(
    """
    <style>
        /* Make dataframes take full width and wrap cleanly */
        [data-testid="stDataFrame"] {
            width: 100% !important;
        }
        [data-testid="stDataFrame"] > div {
            width: 100% !important;
        }
        
        /* Transform Streamlit buttons into gorgeous interactive navigation cards */
        div[data-testid="column"] button {
            border-radius: 24px !important;
            padding: 20px 10px !important;
            height: 120px !important;
            width: 100% !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.03) !important;
            transition: all 0.3s ease !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            white-space: pre-wrap !important;
        }
        div[data-testid="column"] button:hover {
            transform: translateY(-5px) !important;
            box-shadow: 0 8px 25px rgba(0,0,0,0.08) !important;
        }

        /* Individual Card Colors & Borders based on Column Position */
        div[data-testid="column"]:nth-child(1) button {
            background-color: #ffebee !important;
            color: #c2185b !important;
            border: 2px solid #c2185b !important;
        }
        div[data-testid="column"]:nth-child(2) button {
            background-color: #e0f7fa !important;
            color: #00838f !important;
            border: 2px solid #00838f !important;
        }
        div[data-testid="column"]:nth-child(3) button {
            background-color: #f3e5f5 !important;
            color: #7b1fa2 !important;
            border: 2px solid #7b1fa2 !important;
        }
        div[data-testid="column"]:nth-child(4) button {
            background-color: #e8f5e9 !important;
            color: #2e7d32 !important;
            border: 2px solid #2e7d32 !important;
        }
        div[data-testid="column"]:nth-child(5) button {
            background-color: #fff3e0 !important;
            color: #ef6c00 !important;
            border: 2px solid #ef6c00 !important;
        }
    </style>
""",
    unsafe_allow_html=True,
)
# List of core mechanical manufacturing wallpapers
manufacturing_wallpapers = [
    "https://images.unsplash.com/photo-1563770660941-20978e870e26?q=80&w=1920&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1616401784845-180882ba9ba8?q=80&w=1920&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1635835266854-a87d1c6bc1b8?q=80&w=1920&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1531297484001-80022131f5a1?q=80&w=1920&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1581092335397-9583fe92d232?q=80&w=1920&auto=format&fit=crop",
]

selected_wallpaper = random.choice(manufacturing_wallpapers)

# --- INJECT CSS FOR TOP BAR & HORIZONTAL NAVIGATION ---
st.markdown(
    f"""
<style>
    /* Full page background with dynamic mechanical wallpaper on login */
    .stApp {{
        background: linear-gradient(rgba(15, 12, 29, 0.65), rgba(15, 12, 29, 0.85)),
                    url('{selected_wallpaper}');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    .stDeployButton {{display: none !important;}}
    [data-testid="stSidebar"] {{display: none !important;}}

    /* Style Streamlit Form for Glassmorphism */
    div[data-testid="stForm"] {{
        background: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(16px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 20px !important;
        padding: 40px 30px !important;
        box-shadow: 0 30px 60px rgba(0, 0, 0, 0.4) !important;
    }}

    .glass-title {{
        color: #ffffff !important;
        text-align: center;
        font-size: 32px;
        font-weight: 700;
        margin-top: 15px;
        letter-spacing: 1px;
    }}
    .glass-subtitle {{
        color: rgba(255, 255, 255, 0.7) !important;
        text-align: center;
        font-size: 14px;
        margin-bottom: 25px;
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
        border-radius: 8px !important;
        border: none !important;
        height: 48px !important;
        font-size: 16px !important;
        margin-top: 15px !important;
        transition: all 0.3s ease !important;
    }}
    div[data-testid="stFormSubmitButton"] button:hover {{
        background-color: #e2e2e2 !important;
        color: #000000 !important;
        transform: translateY(-2px);
    }}
</style>
""",
    unsafe_allow_html=True,
)


# --- HELPER FUNCTIONS ---
def generate_new_captcha():
    ops = [("+", lambda a, b: a + b), ("-", lambda a, b: a - b), ("*", lambda a, b: a * b)]
    op_symbol, op_func = random.choice(ops)

    if op_symbol == "-":
        a = random.randint(5, 20)
        b = random.randint(1, a)
    elif op_symbol == "*":
        a = random.randint(2, 9)
        b = random.randint(2, 9)
    else:
        a = random.randint(1, 20)
        b = random.randint(1, 20)

    st.session_state.captcha_num1 = a
    st.session_state.captcha_num2 = b
    st.session_state.captcha_op = op_symbol
    st.session_state.captcha_ans = op_func(a, b)


# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "nav_choice" not in st.session_state:
    st.session_state.nav_choice = "Dashboard & Tracking"

if "captcha_num1" not in st.session_state:
    generate_new_captcha()


def login():
    entered_user = st.session_state.get("username", "")
    entered_pass = st.session_state.get("password", "")
    entered_captcha_str = st.session_state.get("captcha_input", "").strip()

    try:
        entered_captcha = int(entered_captcha_str)
    except ValueError:
        st.error("Please enter a valid number for the CAPTCHA.")
        generate_new_captcha()
        return

    if entered_captcha != st.session_state.captcha_ans:
        st.error("Incorrect CAPTCHA answer. Please try again.")
        generate_new_captcha()
    elif entered_user == "admin" and entered_pass == "admin123":
        st.session_state.logged_in = True
        st.success("Login successful!")
        st.rerun()
    else:
        st.error("Invalid username or password. Please try again.")
        generate_new_captcha()


def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.password = ""
    st.session_state.captcha_input = ""
    generate_new_captcha()


# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("login_form"):
            if logo_base64:
                st.markdown(
                    f"""
                    <div style="text-align: center; margin-bottom: 5px;">
                        <img src="data:image/png;base64,{logo_base64}" width="90" style="display: block; margin: 0 auto;" />
                    </div>
                """,
                    unsafe_allow_html=True,
                )

            st.markdown("<div class='glass-title'>KINETIC GEARS</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='glass-subtitle'>Please enter credentials, solve the maths and start the work</div>",
                unsafe_allow_html=True,
            )

            st.text_input("Username", key="username", placeholder="Enter username")
            st.text_input("Password", type="password", key="password", placeholder="Enter password")

            captcha_label = f"Solve: {st.session_state.captcha_num1} {st.session_state.captcha_op} {st.session_state.captcha_num2} = ?"
            st.text_input(captcha_label, key="captcha_input", placeholder="Enter the answer")

            submitted = st.form_submit_button("Log In", use_container_width=True)
            if submitted:
                login()

# --- DASHBOARD SCREEN WITH CUSTOM TOP BAR & HORIZONTAL NAVIGATION ---
else:
    # --- TOP HEADER BAR ---
    top_c1, top_c2, top_c3, top_c4 = st.columns([1.5, 2, 1.5, 1])

    with top_c1:
        st.markdown(
            """
            <div style="color: #ffffff; font-size: 15px; font-weight: 600;">👤 admin</div>
            <div style="color: rgba(255, 255, 255, 0.7); font-size: 13px;">Role: Admin</div>
        """,
            unsafe_allow_html=True,
        )

    with top_c2:
        st.markdown(
            """
            <div style="display: flex; justify-content: center;">
                <div style="background: linear-gradient(135deg, #7c3aed 0%, #3b82f6 100%); padding: 6px 18px; border-radius: 20px; text-align: center; box-shadow: 0 4px 15px rgba(124, 58, 237, 0.4);">
                    <div style="color: #ffffff; font-weight: 700; font-size: 16px; letter-spacing: 1px;">12:37:23 AM</div>
                    <div style="color: rgba(255, 255, 255, 0.9); font-size: 11px;">Thursday, October 15, 2026</div>
                </div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with top_c3:
        st.markdown(
            """
            <div style="text-align: right; color: rgba(255, 255, 255, 0.8); font-size: 13px;">
                ⏳ <b>Expires:</b><br/>09:59
            </div>
        """,
            unsafe_allow_html=True,
        )

    with top_c4:
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()

    st.markdown("<hr style='border-color: rgba(255,255,255,0.15); margin: 15px 0;'>", unsafe_allow_html=True)

    # --- HORIZONTAL NAVIGATION MENU ---
    st.markdown(
        "<div style='color: #ffffff; font-size: 18px; font-weight: 700; margin-bottom: 10px;'>📌 Navigation Menu</div>",
        unsafe_allow_html=True,
    )

    nav_cols = st.columns(5)
    menu_items = [
        ("Dashboard & Tracking", "📊"),
        ("View Drawing (In-Browser)", "🔍"),
        ("Enter Dispatches", "📝"),
        ("Manage Drawings", "📐"),
        ("Add New Item Schedule", "➕"),
    ]

    for i, (item, icon) in enumerate(menu_items):
        with nav_cols[i]:
            is_selected = st.session_state.nav_choice == item
            btn_label = f"{icon} {item}"

            if is_selected:
                # Active button with gradient styling via custom markdown container
                st.markdown(
                    f"""
                    <div style="background: linear-gradient(135deg, #7c3aed 0%, #3b82f6 100%); 
                                padding: 10px 14px; border-radius: 10px; text-align: center; 
                                color: white; font-weight: 600; font-size: 13px; box-shadow: 0 4px 12px rgba(124, 58, 237, 0.4);">
                        {btn_label}
                    </div>
                """,
                    unsafe_allow_html=True,
                )
            else:
                if st.button(btn_label, key=f"nav_{i}", use_container_width=True):
                    st.session_state.nav_choice = item
                    st.rerun()

    st.markdown("<hr style='border-color: rgba(255,255,255,0.15); margin: 20px 0;'>", unsafe_allow_html=True)

    # --- MAIN CONTENT AREA ---
    st.title(f"📊 {st.session_state.nav_choice}")
    st.write(f"Welcome back, **admin**! You are viewing the **{st.session_state.nav_choice}** module.")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="New Clients", value="236", delta="+12.3%")
    with col2:
        st.metric(label="Earnings of Month", value="$18,306", delta="+4.2%")
    with col3:
        st.metric(label="New Projects", value="1538", delta="-1.5%")
    with col4:
        st.metric(label="Active Gear units", value="864")

    st.markdown("---")
