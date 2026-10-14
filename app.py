import random
import streamlit as st

# Set page configuration with title and logo favicon
st.set_page_config(
    page_title="Kinetic Gears",
    page_icon="KG-Logo.png",
    layout="centered"
)


# --- HELPER FUNCTIONS ---
def generate_new_captcha():
    """Generates a random simple arithmetic question."""
    ops = [("+", lambda a, b: a + b), ("-", lambda a, b: a - b), ("*", lambda a, b: a * b)]
    op_symbol, op_func = random.choice(ops)

    if op_symbol == "-":
        a = random.randint(5, 20)
        b = random.randint(1, a)  # Ensure non-negative results for simplicity
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

    # Validate CAPTCHA
    try:
        entered_captcha = int(entered_captcha_str)
    except ValueError:
        st.error("Please enter a valid number for the CAPTCHA.")
        generate_new_captcha()
        return

    if entered_captcha != st.session_state.captcha_ans:
        st.error("Incorrect CAPTCHA answer. Please try again.")
        generate_new_captcha()  # Generate a new puzzle on failure
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
    # Display logo centered above login form
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image("KG-Logo.png", use_container_width=True)

    st.markdown("<h2 style='text-align: center;'>Kinetic Gears</h2>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; color: gray;'>Please enter credentials, solve the maths and start the work</p>",
        unsafe_allow_html=True,
    )

    with st.form("login_form"):
        st.text_input("Username", key="username", placeholder="Enter username")
        st.text_input("Password", type="password", key="password", placeholder="Enter password")

        # Display Arithmetic CAPTCHA question
        captcha_label = f"Solve: {st.session_state.captcha_num1} {st.session_state.captcha_op} {st.session_state.captcha_num2} = ?"
        st.text_input(captcha_label, key="captcha_input", placeholder="Enter the answer")

        submitted = st.form_submit_button("Login", use_container_width=True)
        if submitted:
            login()

# --- DASHBOARD SCREEN (Post-Login) ---
else:
    # Header with logo
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image("KG-Logo.png", width=80)
    with col2:
        st.title("Kinetic Gears Dashboard")

    st.write("You have successfully logged in as **admin**.")
    st.info("This is where your core application features will go.")

    if st.button("Log Out", type="secondary"):
        logout()
        st.rerun()
