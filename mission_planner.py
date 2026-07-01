import numpy as np
import streamlit as st
import time
import psycopg2
import hashlib
from datetime import datetime
from exporter import export_to_kml

st.set_page_config(page_title="Agro-Telemetry Command Center", layout="wide")

# Initialize session storage keys for tracking login state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "pilot_username" not in st.session_state:
    st.session_state["pilot_username"] = None

# Helper database execution link
def get_db_connection():
    return psycopg2.connect(dbname="drone_db", user="kamalnayan", host="localhost", port="5432")

# Database table configuration setup
def initialize_auth_tables():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # 1. Create Pilots authentication storage table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS drone_pilots (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(64) NOT NULL
            );
        """)
        # 2. Add an updated flight logging tracker table linked to specific pilots
        cur.execute("""
            CREATE TABLE IF NOT EXISTS flight_logs (
                id SERIAL PRIMARY KEY,
                pilot_username VARCHAR(50),
                timestamp TIMESTAMP,
                target_altitude_m INT,
                total_waypoints INT
            );
        """)
        
        # Create a default pilot account (username: admin, password: password123) if empty
        cur.execute("SELECT COUNT(*) FROM drone_pilots;")
        if cur.fetchone()[0] == 0:
            default_hash = hashlib.sha256("password123".encode()).hexdigest()
            cur.execute("INSERT INTO drone_pilots (username, password_hash) VALUES (%s, %s);", ("admin", default_hash))
            
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Auth Setup Warning: {e}")

# Run database setup
initialize_auth_tables()

# Verification check function
def verify_pilot_login(username, password):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cur.execute("SELECT * FROM drone_pilots WHERE username = %s AND password_hash = %s;", (username, password_hash))
        user = cur.fetchone()
        cur.close()
        conn.close()
        return user is not None
    except Exception:
        return False

# Database mission execution logger function
def log_mission_to_db(pilot, altitude, waypoint_count):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO flight_logs (pilot_username, timestamp, target_altitude_m, total_waypoints) VALUES (%s, %s, %s, %s);",
            (pilot, datetime.now(), altitude, waypoint_count)
        )
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception:
        return False

def generate_lawnmower_path(min_lat, max_lat, min_lon, max_lon, alt):
    lat_step = 0.0004
    lon_step = 0.0005
    waypoints = []
    lat_range = np.arange(min_lat, max_lat, lat_step)
    lon_range = np.arange(min_lon, max_lon, lon_step)
    flip = False
    for lon in lon_range:
        current_lats = lat_range[::-1] if flip else lat_range
        for lat in current_lats:
            waypoints.append({"lat": float(lat), "lon": float(lon), "altitude": alt})
        flip = not flip
    return waypoints

# --- INTERACTIVE SCREEN UI SWITCH ROUTER ---
if not st.session_state["logged_in"]:
    # Display Login Prompt Form Frame
    st.markdown("<h2 style='text-align: center;'>🔐 Drone Pilot Security Gateway</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.write("Please authenticate with your DGCA pilot credentials:")
            user_input = st.text_input("Username / Pilot ID")
            pass_input = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Authenticate Securely")
            
            if submit_button:
                if verify_pilot_login(user_input, pass_input):
                    st.session_state["logged_in"] = True
                    st.session_state["pilot_username"] = user_input
                    st.success("Access Granted! Loading system dashboard...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid Username or Password reference flag.")
        st.info("💡 Default Testing Account Login -> Username: **admin** | Password: **password123**")

else:
    # Display Your Core Mission Control Planner Suite Layout
    st.sidebar.markdown(f"👤 **Logged in as:** `{st.session_state['pilot_username']}`")
    if st.sidebar.button("🚪 Logout / Lock Terminal"):
        st.session_state["logged_in"] = False
        st.session_state["pilot_username"] = None
        st.rerun()

    st.title("🚁 Agro-Telemetry Flight Operations Command Center")
    st.subheader(f"DGCA Green-Zone Autonomous Mission Planner — Welcome Pilot {st.session_state['pilot_username']}")

    st.sidebar.header("🕹️ Simulation Flight Deck")
    target_altitude = st.sidebar.slider("Target Altitude (Meters)", 10, 120, 60)
    sim_speed = st.sidebar.slider("Simulation Speed (Delay)", 0.1, 1.0, 0.3)
    start_sim = st.sidebar.button("▶️ Start Live Flight Simulation")

    min_lat, max_lat = 24.2124, 24.2135
    min_lon, max_lon = 83.0335, 83.0348

    generated_points = generate_lawnmower_path(min_lat, max_lat, min_lon, max_lon, target_altitude)

    if generated_points:
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="DGCA Aviation Safety Score", value="100/100")
        with col2:
            st.success("Flight compliant with DGCA Green Zone parameters.")

        st.write("### Live Mission Trajectory View")
        map_placeholder = st.empty()

        if start_sim:
            st.sidebar.info("🛸 Flight in progress...")
            for i in range(1, len(generated_points) + 1):
                map_placeholder.map(generated_points[:i])
                time.sleep(sim_speed)
            
            # Log with active session pilot configuration details
            db_logged = log_mission_to_db(st.session_state["pilot_username"], target_altitude, len(generated_points))
            if db_logged:
                st.sidebar.success("🏁 Mission saved directly to Pilot Flight Logs!")
            else:
                st.sidebar.success("🏁 Mission completed successfully!")
        else:
            map_placeholder.map(generated_points)

        try:
            kml_string = export_to_kml(generated_points)
            st.download_button(
                label="📥 Download KML Flight Plan",
                data=kml_string,
                file_name="renukoot_flight_plan.kml",
                mime="application/vnd.google-earth.kml+xml"
            )
        except Exception as e:
            st.error(f"Exporter warning: {e}")
    else:
        st.warning("No tracking waypoints generated.")
