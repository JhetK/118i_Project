import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
from datetime import datetime
import os
from geopy.distance import geodesic

# Set page configuration
st.set_page_config(page_title="San Jose Water Quality Dashboard", layout="centered")

# Custom CSS to reduce spacing between sections
st.markdown("""
    <style>
        .main > div { padding-top: 0.5rem; padding-bottom: 0.5rem; }
        .stButton { margin-top: 1rem; }
        .stTextInput, .stNumberInput, .stDateInput { margin-top: -0.5rem; }
        .stContainer { padding: 1rem 0; }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("San Jose Water Quality Dashboard")

# Known coordinates for San Jose zip codes as fallback
known_zipcode_coords = {
    "95110": (37.3422, -121.8996),
    "95112": (37.3535, -121.8865),
    "95113": (37.3333, -121.8907),
    "95116": (37.3496, -121.8569),
    "95117": (37.3126, -121.9502),
    "95118": (37.2505, -121.8891),
    "95120": (37.2060, -121.8133),
}

# Define path and expected columns for data file
file_path = "san_jose_water_quality_user_data.csv"
expected_columns = ["Zipcode", "Date", "pH", "Turbidity", "Dissolved Oxygen", "Nitrate"]

# Load existing data or create a new file if not present
if not os.path.isfile(file_path):
    pd.DataFrame(columns=expected_columns).to_csv(file_path, index=False)

# Utility functions
def validate_data(pH, turbidity, dissolved_oxygen, nitrate):
    validation_warnings = []
    if not (6.5 <= pH <= 8.5):
        validation_warnings.append("pH level is outside the typical safe range (6.5 - 8.5).")
    if not (0 <= turbidity <= 5):
        validation_warnings.append("Turbidity is outside the typical safe range (0 - 5 NTU).")
    if not (5 <= dissolved_oxygen <= 14):
        validation_warnings.append("Dissolved Oxygen is outside the typical safe range (5 - 14 mg/L).")
    if not (0 <= nitrate <= 10):
        validation_warnings.append("Nitrate level is outside the safe range (0 - 10 mg/L).")
    return validation_warnings

def get_nearest_zipcode(lat, lon):
    min_distance = float("inf")
    nearest_zipcode = None
    for zipcode, coord in known_zipcode_coords.items():
        distance = geodesic((lat, lon), coord).miles
        if distance < min_distance:
            min_distance = distance
            nearest_zipcode = zipcode
    return nearest_zipcode

def get_zipcode_from_coordinates(lat, lon):
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=10&addressdetails=1"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "address" in data and "postcode" in data["address"]:
            return data["address"]["postcode"]
    return get_nearest_zipcode(lat, lon)

# Step 1: Location Selection
st.markdown("### Step 1: Select Your Location")
st.write("Click on the map to choose your location. We’ll detect the zipcode automatically.")
initial_location = [37.3382, -121.8863]
m = folium.Map(location=initial_location, zoom_start=12)
m.add_child(folium.LatLngPopup())
map_output = st_folium(m)  # Removed width and height to use default size
clicked_coordinates = map_output.get("last_clicked", None)
zipcode = ""

if clicked_coordinates:
    lat, lon = clicked_coordinates["lat"], clicked_coordinates["lng"]
    zipcode = get_zipcode_from_coordinates(lat, lon)
    if zipcode:
        st.success(f"Detected Zipcode: {zipcode}")
    else:
        st.warning("Could not find a zipcode for the selected location. Try another point.")

zipcode = st.text_input("Confirm Zipcode", value=zipcode, max_chars=5)

# Step 2: Water Quality Data Entry
st.markdown("### Step 2: Enter Water Quality Data")
date = st.date_input("Date of Measurement", value=datetime.today())
ph_level = st.number_input("pH Level (6.5 - 8.5)", min_value=6.5, max_value=8.5, value=7.0, step=0.1)
turbidity = st.number_input("Turbidity (NTU, 0 - 5 ideal)", min_value=0.0, max_value=10.0, value=1.0, step=0.1)
dissolved_oxygen = st.number_input("Dissolved Oxygen (mg/L, 5 - 14 ideal)", min_value=5.0, max_value=14.0, value=8.0, step=0.1)
nitrate = st.number_input("Nitrate Level (mg/L, 0 - 10 safe)", min_value=0.0, max_value=10.0, value=1.0, step=0.1)

# Submit Data
if st.button("Submit Data"):
    if zipcode:
        validation_warnings = validate_data(ph_level, turbidity, dissolved_oxygen, nitrate)
        if validation_warnings:
            st.warning("Some values seem unusual:")
            for warning in validation_warnings:
                st.write(f"- {warning}")
        else:
            new_data = pd.DataFrame({
                "Zipcode": [zipcode],
                "Date": [date],
                "pH": [ph_level],
                "Turbidity": [turbidity],
                "Dissolved Oxygen": [dissolved_oxygen],
                "Nitrate": [nitrate]
            })
            new_data.to_csv(file_path, mode='a', header=False, index=False)
            st.success("Thank you! Your data has been submitted successfully. ✅")
            st.experimental_set_query_params(rerun=True)
    else:
        st.error("Please enter or confirm a valid zipcode.")

# Recent Data Submissions
st.markdown("---")
st.header("Review Recent Data Submissions")
st.write("Below are the most recent submissions. You can review and delete entries if necessary.")

if os.path.isfile(file_path):
    recent_data = pd.read_csv(file_path, dtype={"Zipcode": str})
    if not recent_data.empty:
        for idx, row in recent_data.tail(5).iterrows():
            entry_text = (f"**Zipcode:** {row['Zipcode']}, **Date:** {row['Date']}, "
                          f"**pH:** {row['pH']}, **Turbidity:** {row['Turbidity']}, "
                          f"**Dissolved Oxygen:** {row['Dissolved Oxygen']}, **Nitrate:** {row['Nitrate']}")
            st.write(entry_text)
            if st.button(f"Delete Entry {idx}", key=f"delete_{idx}"):
                recent_data = recent_data.drop(idx)
                recent_data.to_csv(file_path, index=False)
                st.success("Entry deleted successfully.")
                st.experimental_set_query_params(rerun=True)
    else:
        st.write("No data available yet.")

# Water Quality Analysis
st.markdown("---")
st.header("Water Quality Analysis")
st.write("This analysis helps you understand water quality in your area. Each parameter is explained with safe ranges.")

safe_ranges = {
    "pH": (6.5, 8.5),
    "Turbidity": (0, 5),
    "Dissolved Oxygen": (5, 14),
    "Nitrate": (0, 10)
}

if not recent_data.empty:
    latest_data = recent_data.groupby("Zipcode").mean(numeric_only=True).reset_index()
    for _, row in latest_data.iterrows():
        st.subheader(f"Zipcode: {row['Zipcode']}")
        st.write("Water quality compared to safe ranges:")
        for param, (low, high) in safe_ranges.items():
            value = row[param]
            within_range = low <= value <= high
            icon = "✅" if within_range else "⚠️"
            range_text = f"{low} - {high}"
            st.write(f"- **{param}**: {value:.2f} (Ideal Range: {range_text}) {icon}")
else:
    st.warning("No data available for analysis. Please submit data.")

# Footer
st.markdown("---")
st.write("Developed by Orange Team | Powered by [Streamlit](https://streamlit.io/) and [OpenAI](https://openai.com)")
st.write("For inquiries, contact jhetkenneth.advincula@sjsu.edu")