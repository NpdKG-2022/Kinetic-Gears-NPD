import streamlit as st
import pandas as pd
import random

# Page Configuration
st.set_page_config(
    page_title="KINETIC GEARS | NPD",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# USER DATABASE & CREDENTIALS
# ----------------------------------------------------
USERS = {
    "admin": "admin123"
}

# ----------------------------------------------------
# AUTHENTICATION & CAPTCHA MODULE
# ----------------------------------------------------
def generate_new_captcha():
    """Forces generation of new random numbers for the math CAPTCHA."""
    st.session_state["captcha_num1"] = random.randint(1, 9)
    st.session_state["captcha_num2"] = random.randint(1, 9)

def init_captcha():
    """Initializes CAPTCHA numbers if not already present."""
    if "captcha_num1" not in st.session_state or "captcha_num2" not in st.session_state:
        generate_new_captcha()

def check_credentials():
    """Handles login form with username, password, and dynamic CAPTCHA validation."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("# ⚙️ KINETIC GEARS")
            st.markdown("### New Product Development")
            st.markdown("---")
            st.markdown("#### Authorized Employee Login")
            
            init_captcha()
            
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                
                num1 = st.session_state["captcha_num1"]
                num2 = st.session_state["captcha_num2"]
                captcha_label = f"Security Verification: What is {num1} + {num2}?"
                
                st.markdown(f"**{captcha_label}**")
                user_captcha = st.text_input("Enter Captcha Answer", placeholder="Enter sum")
                
                submit_login = st.form_submit_button("Secure Login", use_container_width=True)
                
                if submit_login:
                    expected_captcha = str(num1 + num2)
                    
                    # Validate CAPTCHA and Credentials
                    if user_captcha.strip() != expected_captcha:
                        st.error("❌ Incorrect CAPTCHA answer. A new verification has been generated.")
                        generate_new_captcha()
                        st.rerun()
                    elif username in USERS and USERS[username] == password:
                        st.session_state["authenticated"] = True
                        st.success("Login successful! Loading portal...")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password. A new verification has been generated.")
                        generate_new_captcha()
                        st.rerun()
            
        return False
    return True

if not check_credentials():
    st.stop()

# ----------------------------------------------------
# STYLING & NAVIGATION (Post-Login)
# ----------------------------------------------------
st.sidebar.image("https://img.icons8.com/external-flat-design-circle/64/external-Gear-industrial-technology-flat-design-circle.png", width=50)
st.sidebar.markdown("### KINETIC GEARS")
st.sidebar.markdown("**New Product Development (N.P.D.)**")
st.sidebar.markdown("---")

nav_selection = st.sidebar.radio(
    "Select Module",
    ["Dashboard", "ISO 8.3.3.1 Design Inputs", "Material & Standards Matrix", "Prototype Cost Estimator"]
)

st.sidebar.markdown("---")
if st.sidebar.button("Log Out"):
    st.session_state["authenticated"] = False
    # Clear captcha so a brand new challenge appears on next login
    if "captcha_num1" in st.session_state:
        del st.session_state["captcha_num1"]
    if "captcha_num2" in st.session_state:
        del st.session_state["captcha_num2"]
    st.rerun()

st.sidebar.info("System Status: **Online** | ISO 9001:2015 Compliant")

# ----------------------------------------------------
# 1. DASHBOARD MODULE
