import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
import os

st.title("San Jose Water Quality Dashboard")

# Define path to the data file
file_path = "san_jose_water_quality_user_data.csv"

# Define safe ranges for each water quality parameter
safe_ranges = {
    "pH": (6.5, 8.5),
    "Turbidity": (0, 5),
    "Dissolved Oxygen": (5, 14),
    "Nitrate": (0, 10)
}

# Check if the data file exists and contains data
if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
    data = pd.read_csv(file_path, parse_dates=["Date"], dtype={"Zipcode": str})
    
    if "Zipcode" in data.columns:
        # Convert relevant columns to numeric, handling non-numeric values as NaN
        for col in ["pH", "Turbidity", "Dissolved Oxygen", "Nitrate"]:
            data[col] = pd.to_numeric(data[col], errors="coerce")
        
        # Drop rows where all relevant columns are NaN to avoid plotting issues
        data = data.dropna(subset=["pH", "Turbidity", "Dissolved Oxygen", "Nitrate"], how="all")

        # Summary Statistics Section
        st.header("Summary Statistics")
        if not data.empty and data.select_dtypes(include="number").shape[1] > 0:
            summary = data.describe()
            st.dataframe(summary)
        else:
            st.warning("No numeric data available for summary statistics.")

        # Water Quality Alerts
        st.header("Water Quality Alerts by Zipcode")
        for param, (low, high) in safe_ranges.items():
            st.write(f"**{param}**")
            exceed = data[(data[param] < low) | (data[param] > high)]
            if not exceed.empty:
                st.write(exceed[["Zipcode", "Date", param]])
            else:
                st.write("All values within safe limits.")

        # Trends Over Time Section
        st.header("Trends Over Time for Key Parameters")
        fig, axs = plt.subplots(2, 2, figsize=(12, 8))

        # Check for numeric data in each plot and handle empty cases gracefully
        if not data["pH"].dropna().empty:
            data.groupby("Date")["pH"].mean().plot(ax=axs[0, 0], title="Average pH Level Over Time", color="blue")
            axs[0, 0].axhline(y=safe_ranges["pH"][0], color="green", linestyle="--")
            axs[0, 0].axhline(y=safe_ranges["pH"][1], color="green", linestyle="--")
        else:
            axs[0, 0].text(0.5, 0.5, 'No pH data available', horizontalalignment='center', verticalalignment='center')

        if not data["Turbidity"].dropna().empty:
            data.groupby("Date")["Turbidity"].mean().plot(ax=axs[0, 1], title="Average Turbidity Over Time", color="orange")
            axs[0, 1].axhline(y=safe_ranges["Turbidity"][1], color="green", linestyle="--")
        else:
            axs[0, 1].text(0.5, 0.5, 'No Turbidity data available', horizontalalignment='center', verticalalignment='center')

        if not data["Dissolved Oxygen"].dropna().empty:
            data.groupby("Date")["Dissolved Oxygen"].mean().plot(ax=axs[1, 0], title="Average Dissolved Oxygen Over Time", color="green")
            axs[1, 0].axhline(y=safe_ranges["Dissolved Oxygen"][0], color="green", linestyle="--")
            axs[1, 0].axhline(y=safe_ranges["Dissolved Oxygen"][1], color="green", linestyle="--")
        else:
            axs[1, 0].text(0.5, 0.5, 'No Dissolved Oxygen data available', horizontalalignment='center', verticalalignment='center')

        if not data["Nitrate"].dropna().empty:
            data.groupby("Date")["Nitrate"].mean().plot(ax=axs[1, 1], title="Average Nitrate Level Over Time", color="red")
            axs[1, 1].axhline(y=safe_ranges["Nitrate"][1], color="green", linestyle="--")
        else:
            axs[1, 1].text(0.5, 0.5, 'No Nitrate data available', horizontalalignment='center', verticalalignment='center')

        plt.tight_layout()
        st.pyplot(fig)

        # Interactive Map of Water Quality
        st.header("Water Quality Map by Zipcode")
        
        # Known coordinates for San Jose zip codes
        known_zipcode_coords = {
            "95110": (37.3422, -121.8996),
            "95112": (37.3535, -121.8865),
            "95113": (37.3333, -121.8907),
            "95116": (37.3496, -121.8569),
            "95117": (37.3126, -121.9502),
            "95118": (37.2505, -121.8891),
            "95120": (37.2060, -121.8133),
            # Additional zip codes as needed
        }
        
        # Calculate average water quality values by zipcode
        zipcode_summary = data.groupby("Zipcode").mean(numeric_only=True).reset_index()
        
        # Initialize a folium map centered on San Jose
        m = folium.Map(location=[37.3382, -121.8863], zoom_start=11)

        # Add markers for each zipcode based on turbidity level
        for idx, row in zipcode_summary.iterrows():
            zipcode = str(row["Zipcode"])
            if zipcode in known_zipcode_coords:
                lat, lon = known_zipcode_coords[zipcode]
                
                # Determine marker color based on turbidity
                color = "green" if row["Turbidity"] <= safe_ranges["Turbidity"][1] else "red"
                
                # Define popup information for the marker
                popup_info = (
                    f"<b>Zipcode:</b> {zipcode}<br>"
                    f"<b>Average pH:</b> {row['pH']:.2f}<br>"
                    f"<b>Average Turbidity:</b> {row['Turbidity']:.2f} NTU<br>"
                    f"<b>Average Dissolved Oxygen:</b> {row['Dissolved Oxygen']:.2f} mg/L<br>"
                    f"<b>Average Nitrate:</b> {row['Nitrate']:.2f} mg/L"
                )
                
                # Add marker to map
                folium.Marker(
                    location=[lat, lon],
                    popup=popup_info,
                    icon=folium.Icon(color=color)
                ).add_to(m)
        
        # Display the interactive map in Streamlit
        st_folium(m, width=700, height=500)

    else:
        st.error("The data file is missing the 'Zipcode' column. Please check the data file format.")
else:
    st.warning("No data available. Please ensure data is submitted for analysis.")

# Footer with Additional Links
st.markdown("---")
st.write("Developed by Orange Team | Powered by [Streamlit](https://streamlit.io/) and [OpenAI](https://openai.com)")
st.write("For inquiries, contact jhetkenneth.advincula@sjsu.edu (mailto:your.email@company.com)")