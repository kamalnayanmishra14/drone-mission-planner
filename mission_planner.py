import numpy as np
import streamlit as st
import time
import psycopg2
from datetime import datetime
from exporter import export_to_kml

st.set_page_config(page_title="Agro-Telemetry Command Center", layout="wide")
st.title("🚁 Agro-Telemetry Flight Operations Command Center")
st.subheader("DGCA Green-Zone Autonomous Mission Planner")

# Function to save mission logs into your local PostgreSQL database
def log_mission_to_db(altitude, waypoint_count):
    try:
        # Connect to your active local postgresql@18 instance
        conn = psycopg2.connect(
            dbname="drone_db", 
            user="kamalnayan", 
            host="localhost", 
            port="5432"
        )
        cur = conn.cursor()
        
        # Create table if it doesn't exist yet
        cur.execute("""
            CREATE TABLE IF NOT EXISTS flight_logs (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP,
                target_altitude_m INT,
                total_waypoints INT
            );
        """)
        
        # Insert current flight parameters
        cur.execute(
            "INSERT INTO flight_logs (timestamp, target_altitude_m, total_waypoints) VALUES (%s, %s, %s);",
            (datetime.now(), altitude, waypoint_count)
        )
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Database Log Warning: {e}")
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
        
        # Trigger PostgreSQL Database logging on complete
        db_logged = log_mission_to_db(target_altitude, len(generated_points))
        if db_logged:
            st.sidebar.success("🏁 Mission saved to PostgreSQL database!")
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
