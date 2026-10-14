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
        <h1 style="font-size: 50px; margin-bottom: 0px; color: white;">Welcome to KINETIC GEARS</h1>
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
