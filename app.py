import base64
import random
import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="Kinetic Gears",
    page_icon="KG-Logo.png",
    layout="centered"
)


# Helper function to convert logo to base64 for flawless HTML centering
@st.cache_data
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return ""


logo_base64 = get_base64_image("KG-Logo.png")

# --- INJECT GLASSMORPHISM CSS ---
st.markdown("""
<style>
    /* Full page background with mountain theme */
    .stApp {
        background: linear-gradient(rgba(15, 12, 29, 0.5), rgba(15, 12, 29, 0.7)),
                    url('https://images.unsplash.com/photo-1506744038136-46273834b3fb?q=80&w=1920&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* Hide standard header & footer decoration */
    header, footer {
        visibility: hidden;
    }

    /* Style Streamlit Form to look like a Frosted Glass Card */
    div[data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(16px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 20px !important;
        padding: 40px 30px !important;
        box-shadow: 0 30px 60px rgba(0, 0, 0, 0.4) !important;
    }

    /* Custom Title & Subtitle Styling */
    .glass-title {
        color: #ffffff !important;
        text-align: center;
        font-size: 32px;
        font-weight: 700;
        margin-top: 15px;
        letter-spacing: 1px;
    }
    .glass-subtitle {
        color: rgba(255, 255, 255, 0.7) !important;
        text-align: center;
        font-size: 14px;
        margin-bottom: 25px;
    }

    /* Minimalist underline input fields */
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

    /* White Solid Login Button */
    div[data-testid="stFormSubmitButton"] button {
        background-color: #ffffff !important;
        color: #111111 !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        border: none !important;
        height: 48px !important;
        font-size: 16px !important;
        margin-top: 15px !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stFormSubmitButton"] button:hover {
        background-color: #e2e2e2 !important;
        color: #000000 !important;
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)


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


# Function to handle login
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
    else:
        st.error("Invalid username or password. Please try again.")
        generate_new_captcha()


# Function to handle logout
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.password = ""
    st.session_state.captcha_input = ""
    generate_new_captcha()


# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    with st.form("login_form"):
        # Perfectly center the logo using base64 and HTML
        if logo_base64:
            st.markdown(f"""
                <div style="text-align: center; margin-bottom: 5px;">
                    <img src="data:image/png;base64,{logo_base64}" width="90" style="display: block; margin: 0 auto;" />
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<div class='glass-title'>KINETIC GEARS</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='glass-subtitle'>Please enter credentials, solve the maths and start the work</div>",
            unsafe_allow_html=True,
        )

        st.text_input("Username", key="username", placeholder="Enter username")
        st.text_input("Password", type="password", key="password", placeholder="Enter password")

        # Display Arithmetic CAPTCHA question
        captcha_label = f"Solve: {st.session_state.captcha_num1} {st.session_state.captcha_op} {st.session_state.captcha_num2} = ?"
        st.text_input(captcha_label, key="captcha_input", placeholder="Enter the answer")

        submitted = st.form_submit_button("Log In", use_container_width=True)
        if submitted:
            login()

# --- DASHBOARD SCREEN (Post-Login) ---
else:
    st.markdown("<h1 style='color: white;'>📊 Kinetic Gears Dashboard</h1>", unsafe_allow_html=True)
    st.write("You have successfully logged in as **admin**.")
    st.info("This is where your core application features will go.")

    if st.button("Log Out", type="secondary"):
        logout()
        st.rerun()
