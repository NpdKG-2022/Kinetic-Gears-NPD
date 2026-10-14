import streamlit as st
import pandas as pd
import random
import streamlit.components.v1 as components

# Page Configuration
st.set_page_config(
    page_title="KINETIC GEARS | NPD Portal",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Completely hide Streamlit's native sidebar and collapse button globally
st.markdown("""
<style>
  [data-testid="stSidebar"] { display: none !important; }
  [data-testid="collapsedControl"] { display: none !important; }
  .main .block-container { padding-left: 90px; }
</style>
""", unsafe_allow_html=True)
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
    st.session_state["captcha_num1"] = random.randint(1, 9)
    st.session_state["captcha_num2"] = random.randint(1, 9)

def init_captcha():
    if "captcha_num1" not in st.session_state or "captcha_num2" not in st.session_state:
        generate_new_captcha()

def check_credentials():
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
                user_captcha = st.text_input("Enter Captcha Answer", placeholder="Enter the correct answer")
                submit_login = st.form_submit_button("Secure Login", use_container_width=True)
                
                if submit_login:
                    expected_captcha = str(num1 + num2)
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

# Initialize Navigation Session State
if "nav_sel" not in st.session_state:
    st.session_state["nav_sel"] = "Dashboard"

# Handle Navigation & Logout query parameters from custom HTML components
query_params = st.query_params
if query_params.get("nav"):
    st.session_state["nav_sel"] = query_params.get("nav")
    st.query_params.clear()
    st.rerun()

if query_params.get("action") == "logout":
    st.session_state["authenticated"] = False
    st.query_params.clear()
    if "captcha_num1" in st.session_state:
        del st.session_state["captcha_num1"]
    if "captcha_num2" in st.session_state:
        del st.session_state["captcha_num2"]
    st.rerun()

# ----------------------------------------------------
# TOP-RIGHT MINIMAL LIVE CLOCK, WEATHER & LOGOUT
# ----------------------------------------------------
top_bar_html = """
<div id="top-right-container">
  <div id="compact-clock-widget">
    <span id="c-day">---</span>, 
    <span id="c-date">--- 00 0000</span> | 
    <span id="c-time">00:00:00</span> <span id="c-ampm">--</span> | 
    <span id="c-temp">--°C</span>
  </div>
  <button id="logout-btn" onclick="triggerLogout()" title="Log Out">
    <svg xmlns="http://www.w3.org/2000/svg" height="14" width="14" viewBox="0 0 512 512" fill="#f85149" style="min-width: 14px;"><path d="M377.9 105.9L500.7 228.7c7.2 7.2 11.3 17.1 11.3 27.3s-4.1 20.1-11.3 27.3L377.9 406.1c-15 15-41 4.4-41-17.1l0-111-224 0c-17.7 0-32-14.3-32-32l0-32c0-17.7 14.3-32 32-32l224 0 0-111c0-21.5 26-32.1 41-17.1zM64 32c0-17.7 14.3-32 32-32l96 0c17.7 0 32 14.3 32 32s-14.3 32-32 32L96 64c-17.7 0-32 14.3-32 32l0 320c0 17.7 14.3 32 32 32l96 0c17.7 0 32 14.3 32 32s-14.3 32-32 32l-96 0c-35.3 0-64-28.7-64-64L0 96C0 60.7 28.7 32 64 32z"/></svg>
    <span class="logout-text">Log Out</span>
  </button>
</div>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&display=swap');
  body { background: transparent; margin: 0; }
  #top-right-container {
    position: absolute;
    top: 0px;
    right: 0px;
    display: flex;
    align-items: center;
    gap: 8px;
    z-index: 999999;
  }
  #compact-clock-widget {
    background: rgba(13, 17, 23, 0.95);
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 14px;
    font-family: 'Orbitron', sans-serif;
    font-size: 0.75rem;
    color: #e6edf3;
    display: flex;
    gap: 10px;
    align-items: center;
    box-shadow: 0 3px 10px rgba(0,0,0,0.6);
    backdrop-filter: blur(4px);
    height: 30px;
  }
  #compact-clock-widget #c-time { color: #58a6ff; font-weight: 700; }
  #compact-clock-widget #c-ampm { color: #58a6ff; font-weight: 700; }
  #compact-clock-widget #c-temp { color: #3fb950; font-weight: 700; }

  #logout-btn {
    background: rgba(13, 17, 23, 0.95);
    border: 1px solid #30363d;
    border-radius: 6px;
    color: #f85149;
    padding: 0 10px;
    font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.6);
    backdrop-filter: blur(4px);
    overflow: hidden;
    white-space: nowrap;
    width: 34px;
    min-width: 34px;
    height: 30px;
    transition: width 0.25s ease, background 0.2s ease, padding 0.25s ease;
  }
  #logout-btn .logout-text {
    opacity: 0;
    width: 0px;
    overflow: hidden;
    transition: opacity 0.2s ease, width 0.25s ease;
  }
  #logout-btn:hover {
    width: 94px;
    padding: 0 12px;
    background: rgba(48, 54, 61, 0.95);
  }
  #logout-btn:hover .logout-text {
    opacity: 1;
    width: auto;
  }
</style>
<script>
  function updateCompactClock() {
    const now = new Date();
    const days = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"];
    document.getElementById("c-day").innerText = days[now.getDay()];
    let hours = now.getHours();
    const ampm = hours >= 12 ? "PM" : "AM";
    hours = hours % 12;
    hours = hours ? hours : 12;
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    document.getElementById("c-time").innerText = `${String(hours).padStart(2, '0')}:${minutes}:${seconds}`;
    document.getElementById("c-ampm").innerText = ampm;
    const months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];
    document.getElementById("c-date").innerText = `${months[now.getMonth()]} ${String(now.getDate()).padStart(2, '0')} ${now.getFullYear()}`;
  }
  setInterval(updateCompactClock, 1000);
  updateCompactClock();

  async function fetchCompactWeather() {
    try {
      const ipRes = await fetch('https://ipapi.co/json/');
      const ipData = await ipRes.json();
      const lat = ipData.latitude;
      const lon = ipData.longitude;
      if (lat && lon) {
        const weatherRes = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true`);
        const weatherData = await weatherRes.json();
        const temp = weatherData.current_weather.temperature;
        document.getElementById("c-temp").innerText = `${temp}°C`;
      }
    } catch (e) {
      document.getElementById("c-temp").innerText = "--°C";
    }
  }
  fetchCompactWeather();
  setInterval(fetchCompactWeather, 600000);

  function triggerLogout() {
    const url = new URL(window.parent.location.href);
    url.searchParams.set('action', 'logout');
    window.parent.location.href = url.toString();
  }
</script>
"""
components.html(top_bar_html, height=38, scrolling=False)

# ----------------------------------------------------
# MODERN HOVER-EXPANDABLE SIDEBAR (HTML/CSS Component)
# ----------------------------------------------------
current_nav = st.session_state["nav_sel"]

sidebar_html = f"""
<div class="custom-sidebar">
  <div class="brand-container">
    <div class="brand-logo">KG</div>
    <div class="brand-text">
      <div class="brand-title">KINETIC GEARS</div>
      <div class="brand-subtitle">NPD Portal</div>
    </div>
  </div>
  
  <div class="nav-menu">
    <a href="?nav=Dashboard" target="_self" class="nav-item {'active' if current_nav == 'Dashboard' else ''}">
      <span class="icon">📊</span>
      <span class="label">Dashboard</span>
    </a>
    <a href="?nav=ISO 8.3.3.1 Design Inputs" target="_self" class="nav-item {'active' if current_nav == 'ISO 8.3.3.1 Design Inputs' else ''}">
      <span class="icon">📋</span>
      <span class="label">ISO 8.3.3.1 Inputs</span>
    </a>
    <a href="?nav=Material & Standards Matrix" target="_self" class="nav-item {'active' if current_nav == 'Material & Standards Matrix' else ''}">
      <span class="icon">🔬</span>
      <span class="label">Materials Matrix</span>
    </a>
    <a href="?nav=Prototype Cost Estimator" target="_self" class="nav-item {'active' if current_nav == 'Prototype Cost Estimator' else ''}">
      <span class="icon">🧮</span>
      <span class="label">Cost Estimator</span>
    </a>
  </div>

  <div class="sidebar-footer">
    <div class="status-dot"></div>
    <span class="status-text">System Online</span>
  </div>
</div>

<style>
  body {{ background: transparent; margin: 0; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }}
  
  .custom-sidebar {{
    position: fixed;
    top: 10px;
    left: 10px;
    width: 68px;
    height: calc(100vh - 20px);
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 16px;
    box-shadow: 4px 0 20px rgba(0,0,0,0.5);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 20px 12px;
    box-sizing: border-box;
    overflow: hidden;
    transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 99999;
  }}
  
  .custom-sidebar:hover {{
    width: 260px;
  }}

  .brand-container {{
    display: flex;
    align-items: center;
    gap: 14px;
    padding-bottom: 20px;
    border-bottom: 1px solid #30363d;
    white-space: nowrap;
  }}

  .brand-logo {{
    min-width: 44px;
    height: 44px;
    background: linear-gradient(135deg, #f85149, #da3633);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 800;
    font-size: 1.1rem;
    box-shadow: 0 4px 12px rgba(248, 81, 73,.4);
  }}

  .brand-text {{
    opacity: 0;
    transition: opacity 0.2s ease;
  }}

  .custom-sidebar:hover .brand-text {{
    opacity: 1;
  }}

  .brand-title {{
    color: #e6edf3;
    font-weight: 700;
    font-size: 0.95rem;
  }}

  .brand-subtitle {{
    color: #8b949e;
    font-size: 0.75rem;
  }}

  .nav-menu {{
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-top: 15px;
  }}

  .nav-item {{
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 12px 14px;
    border-radius: 10px;
    color: #8b949e;
    text-decoration: none;
    font-weight: 500;
    font-size: 0.88rem;
    white-space: nowrap;
    transition: background 0.2s, color 0.2s;
  }}

  .nav-item:hover {{
    background: rgba(48, 54, 61, 0.5);
    color: #e6edf3;
  }}

  .nav-item.active {{
    background: #21262d;
    color: #58a6ff;
    border-left: 3px solid #58a6ff;
  }}

  .nav-item .icon {{
    font-size: 1.2rem;
    min-width: 24px;
    text-align: center;
  }}

  .nav-item .label {{
    opacity: 0;
    transition: opacity 0.2s ease;
  }}

  .custom-sidebar:hover .nav-item .label {{
    opacity: 1;
  }}

  .sidebar-footer {{
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 12px 14px;
    background: #0d1117;
    border-radius: 10px;
    border: 1px solid #30363d;
    white-space: nowrap;
  }}

  .status-dot {{
    width: 10px;
    height: 10px;
    min-width: 10px;
    background: #3fb950;
    border-radius: 50%;
    box-shadow: 0 0 8px #3fb950;
  }}

  .status-text {{
    color: #8b949e;
    font-size: 0.8rem;
    font-weight: 600;
    opacity: 0;
    transition: opacity 0.2s ease;
  }}

  .custom-sidebar:hover .status-text {{
    opacity: 1;
  }}
</style>
"""

# Render custom sidebar and hide Streamlit's default sidebar
st.sidebar.markdown("""
<style>
  [data-testid="stSidebar"] {{ display: none; }}
  .main {{ margin-left: 40px; }}
</style>
""", unsafe_allow_html=True)

components.html(sidebar_html, height=700, scrolling=False)

nav_selection = st.session_state["nav_sel"]

# ----------------------------------------------------
# 1. DASHBOARD MODULE
# ----------------------------------------------------
if nav_selection == "Dashboard":
    st.markdown("## 📊 NPD Project Dashboard")
    st.markdown("Monitor active gear development pipelines across Stage-Gate milestones.")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Active Projects", value="6")
    with col2:
        st.metric(label="Stage-Gate 3 (Design)", value="2")
    with col3:
        st.metric(label="Prototyping", value="3")
    with col4:
        st.metric(label="Validation & Testing", value="1")

    st.markdown("### Active NPD Pipeline")
    data = {
        "Project ID": ["PRJ-2026-01", "PRJ-2026-02", "PRJ-2026-03", "PRJ-2026-04"],
        "Gear Assembly": ["High-Torque Planetary Carrier", "Helical Drive Pinion", "Bevel Gear Set 3:1", "Spur Gear Module 4"],
        "Current Stage": ["Design Input Review", "Prototype Machining", "Surface Roughness Testing", "Feasibility Study"],
        "Lead Engineer": ["A. Sharma", "R. Verma", "M. Kulkarni", "S. Patil"],
        "Target Date": ["2026-11-30", "2026-10-15", "2026-12-15", "2027-01-20"]
    }
    st.dataframe(pd.DataFrame(data), use_container_width=True)

# ----------------------------------------------------
# 2. ISO 8.3.3.1 DESIGN INPUTS MANAGER
# ----------------------------------------------------
elif nav_selection == "ISO 8.3.3.1 Design Inputs":
    st.markdown("## 📋 Product Design Inputs (Clause 8.3.3.1)")
    st.markdown("Capture functional, performance, safety, and statutory requirements for new gear mechanisms.")

    with st.form("design_input_form"):
        col1, col2 = st.columns(2)
        with col1:
            project_code = st.text_input("Project Code / Gear Model", "KG-SPUR-2026")
            functional_req = st.text_area("Functional & Performance Requirements", "Must withstand continuous torque of 450 Nm at 1500 RPM.")
            safety_statutory = st.text_area("Statutory & Regulatory Requirements", "Compliance with AGMA 2001-D04 and ISO 1328-1 grade 6 accuracy.")
        with col2:
            material_pref = st.text_input("Preferred Material & Heat Treatment", "Case-hardened Steel 20 (GOST 1050-74 / SAE 8620), HRC 58-62")
            tolerance_specs = st.text_area("Critical Dimensional Tolerances", "Bore diameter tolerance H7, face width ±0.05 mm.")
            submitted_by = st.text_input("Lead Designer / Reviewer", "NPD Engineering Team")

        submitted = st.form_submit_button("Save & Log Design Input")
        if submitted:
            st.success(f"Design inputs successfully logged for project {project_code} under ISO 8.3.3.1 compliance standards.")

# ----------------------------------------------------
# 3. MATERIAL & STANDARDS MATRIX
# ----------------------------------------------------
elif nav_selection == "Material & Standards Matrix":
    st.markdown("## 🔬 Material & Standards Cross-Reference")
    st.markdown("Quick lookup matrix for carbon steels, spring wires, industrial sealing elements, and international standards.")

    search_query = st.text_input("Search standard (e.g., GOST 1050-74, SAE 1018, Spring Wire):")

    standards_data = {
        "Material / Standard": [
            "Steel 20 (GOST 1050-74)", 
            "SAE 1018 / 1020", 
            "GOST 9389-75 (Class II)", 
            "Champion Style 59 Sheet", 
            "GOST 6309-73 Thread"
        ],
        "Category": [
            "Carbon Steel", 
            "Carbon Steel", 
            "High-Carbon Spring Wire", 
            "Jointing Sheet", 
            "Sealing Thread"
        ],
        "Key Application": [
            "Gear blanks, shafts", 
            "General machining", 
            "Compression/tension springs", 
            "Oil-resistant gaskets", 
            "Industrial packing"
        ],
        "Equivalent / Notes": [
            "Comparable to AISI 1020", 
            "Standard low-carbon steel", 
            "Cold-drawn carbon spring wire", 
            "0.5 mm oil-resistant jointing", 
            "Black glossy cotton thread"
        ]
    }
    std_df = pd.DataFrame(standards_data)

    if search_query:
        filtered_df = std_df[std_df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.dataframe(std_df, use_container_width=True)

# ----------------------------------------------------
# 4. PROTOTYPE COST ESTIMATOR
# ----------------------------------------------------
elif nav_selection == "Prototype Cost Estimator":
    st.markdown("## 🧮 Prototype & Feasibility Cost Calculator")
    st.markdown("Estimate raw material, cutting/machining time, and scrap overhead for new gear prototypes.")

    col1, col2 = st.columns(2)
    with col1:
        raw_weight = st.number_input("Estimated Blank Weight (kg)", min_value=0.1, max_value=50.0, value=3.5)
        material_cost_per_kg = st.number_input("Material Rate ($/kg)", min_value=1.0, max_value=500.0, value=45.0)
        machining_hours = st.number_input("Estimated Machining / Hobbing Hours", min_value=0.5, max_value=100.0, value=6.0)
    with col2:
        hourly_rate = st.number_input("Machining Hourly Rate ($/hr)", min_value=10.0, max_value=200.0, value=50.0)
        scrap_allowance = st.slider("Scrap & Setup Allowance (%)", 5, 30, 15)

    if st.button("Calculate Prototype Cost"):
        base_material_cost = raw_weight * material_cost_per_kg
        machining_cost = machining_hours * hourly_rate
        subtotal = base_material_cost + machining_cost
        total_cost = subtotal * (1 + scrap_allowance / 100.0)

        st.markdown("---")
        st.markdown("### Cost Breakdown Summary")
        st.metric(label="Total Estimated Prototype Cost", value=f"${total_cost:.2f}")
        st.write(f"- **Raw Material Cost:** ${base_material_cost:.2f}")
        st.write(f"- **Machining Labor Cost:** ${machining_cost:.2f}")
        st.write(f"- **Scrap Buffer ({scrap_allowance}%):** ${(subtotal * scrap_allowance / 100.0):.2f}")
