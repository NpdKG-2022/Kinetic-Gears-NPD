import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="Admin Login",
    page_icon="🔒",
    layout="centered"
)

# Initialize session state for login status if it doesn't exist
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Function to handle login
def login():
    if st.session_state.username == "admin" and st.session_state.password == "admin123":
        st.session_state.logged_in = True
        st.success("Login successful!")
    else:
        st.error("Invalid username or password. Please try again.")

# Function to handle logout
def logout():
    st.session_state.logged_in = False
    # Clear input fields by resetting them if needed
    st.session_state.username = ""
    st.session_state.password = ""

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center;'>🔒 Admin Login</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Please sign in to access the dashboard</p>", unsafe_allow_html=True)
    
    # Use a form so pressing Enter triggers the login button
    with st.form("login_form"):
        st.text_input("Username", key="username", placeholder="Enter username")
        st.text_input("Password", type="password", key="password", placeholder="Enter password")
        
        submitted = st.form_submit_button("Login", use_container_width=True)
        if submitted:
            login()

# --- DASHBOARD SCREEN (Post-Login) ---
else:
    st.title("📊 Welcome to the Admin Dashboard")
    st.write("You have successfully logged in as **admin**.")
    
    # Put your main app content here
    st.info("This is where your core application features will go.")
    
    if st.button("Log Out", type="secondary"):
        logout()
        st.rerun()
