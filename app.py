import base64
import random
import streamlit as st

# Set page configuration
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

# List of core mechanical manufacturing wallpapers
manufacturing_wallpapers = [
    "https://images.unsplash.com/photo-1563770660941-20978e870e26?q=80&w=1920&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1616401784845-180882ba9ba8?q=80&w=1920&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1635835266854-a87d1c6bc1b8?q=80&w=1920&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1531297484001-80022131f5a1?q=80&w=1920&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1581092335397-9583fe92d232?q=80&w=1920&auto=format&fit=crop",
]

selected_wallpaper = random.choice(manufacturing_wallpapers)

# --- INJECT CSS WITH CUSTOM GRADIENT ACTIVE SIDEBAR BUTTON ---
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

    /* --- SIDEBAR RADIO BUTTON GRADIENT PILL STYLING --- */
    div[data-testid="stSidebar"] div[data-testid="stRadio"] label {{
        border-radius: 12px !important;
        padding: 6px 12px !important;
        margin-bottom: 4px !important;
        transition: all 0.2s ease-in-out !important;
    }}

    /* Style for the selected radio button option */
    div[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-baseweb="radio"] input:checked + div {{
        background: transparent !important;
    }}

    div[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) {{
        background: linear-gradient(135deg, #7c3aed 0%, #3b82f6 100%) !important;
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.4);
    }}

    div[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) p {{
        color: #ffffff !important;
        font-weight: 600 !important;
    }}

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

# --- DASHBOARD SCREEN ---
else:
    # --- SIDEBAR NAVIGATION ---
    with st.sidebar:
        if logo_base64:
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
                    <img src="data:image/png;base64,{logo_base64}" width="36" />
                    <h3 style="margin: 0;">Kinetic Gears</h3>
                </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("**MAIN MENU**")
        nav_selection = st.radio(
            "Navigation",
            [
                "🏠 Dashboard",
                "🎫 Ticket List",
                "💬 Chat",
                "📅 Calendar",
                "📋 Forms",
                "📊 Tables",
                "📈 Charts",
                "⚙️ UI Elements",
                "💳 Cards",
            ],
            label_visibility="collapsed",
        )

        st.markdown("---")
        st.markdown("**SESSION**")
        if st.button("🚪 Log Out", use_container_width=True):
            logout()
            st.rerun()

    # --- MAIN DASHBOARD CONTENT AREA ---
    st.title(f"📊 {nav_selection}")
    st.write("Welcome back, **admin**! You are logged into the Kinetic Gears management platform.")

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
    st.info(
        "💡 Whichever navigation item you click in the sidebar will instantly highlight with that gorgeous purple-blue gradient pill background!"
    )
