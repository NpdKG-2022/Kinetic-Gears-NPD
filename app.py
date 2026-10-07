import streamlit as st
import pandas as pd
import random
import streamlit.components.v1 as components

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

# ----------------------------------------------------
# TOP-RIGHT MINIMAL LIVE CLOCK & WEATHER WIDGET
# ----------------------------------------------------
compact_clock_html = """
<div id="compact-clock-widget">
  <span id="c-day">---</span>, 
  <span id="c-date">--- 00 0000</span> | 
  <span id="c-time">00:00:00</span> <span id="c-ampm">--</span> | 
  <span id="c-temp">--°C</span>
</div>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&display=swap');
  body { background: transparent; margin: 0; }
  #compact-clock-widget {
    position: absolute;
    top: 0px;
    right: 0px;
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
  }
  #compact-clock-widget #c-time {
    color: #58a6ff;
    font-weight: 700;
  }
  #compact-clock-widget #c-ampm {
    color: #58a6ff;
    font-weight: 700;
  }
  #compact-clock-widget #c-temp {
    color: #3fb950;
    font-weight: 700;
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
</script>
"""
components.html(compact_clock_html, height=38, scrolling=False)

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
    if "captcha_num1" in st.session_state:
        del st.session_state["captcha_num1"]
    if "captcha_num2" in st.session_state:
        del st.session_state["captcha_num2"]
    st.rerun()

st.sidebar.info("System Status: **Online**")

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
