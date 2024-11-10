import streamlit as st
import pandas as pd
import os

st.title("San Jose Water Quality - Learning Dashboard")

st.header("Why Water Quality Matters")
st.write("Water quality impacts health, the environment, and even the taste of drinking water. "
         "This dashboard provides easy-to-understand insights into different water quality parameters, "
         "so you can learn why these values are important and how they affect daily life.")

# File path to the data
file_path = "san_jose_water_quality_user_data.csv"

# Define explanations, icons, and tips for each parameter
learning_info = {
    "pH": {
        "importance": "The pH level affects taste and safety of water. Ideal pH prevents plumbing corrosion and ensures safety.",
        "health_effects": "Extremely high or low pH can cause skin irritation and affect taste.",
        "ideal_range": "A pH level between 6.5 and 8.5 is generally safe for drinking.",
        "tips": "Consider water treatment options if your pH is out of range.",
        "icon": "⚖️"
    },
    "Turbidity": {
        "importance": "Turbidity indicates how clear the water is. High turbidity can mean contamination.",
        "health_effects": "Clear water is less likely to contain harmful microorganisms.",
        "ideal_range": "Turbidity levels below 5 NTU are considered safe.",
        "tips": "If water looks cloudy, avoid drinking it until filtered or tested.",
        "icon": "💧"
    },
    "Dissolved Oxygen": {
        "importance": "Dissolved oxygen supports aquatic life and enhances taste.",
        "health_effects": "Higher dissolved oxygen is good for taste, though low levels don't directly harm humans.",
        "ideal_range": "Between 5 and 14 mg/L is ideal.",
        "tips": "Low dissolved oxygen may indicate stagnant water. Consider alternative sources.",
        "icon": "🌬️"
    },
    "Nitrate": {
        "importance": "High nitrate can be harmful, particularly to infants and pregnant women.",
        "health_effects": "Excessive nitrate levels can lead to health issues, especially for babies.",
        "ideal_range": "Below 10 mg/L is generally safe.",
        "tips": "Avoid using water with high nitrate for drinking, especially for infants.",
        "icon": "🌱"
    }
}

# Define safe ranges for displaying health indicators
safe_ranges = {
    "pH": (6.5, 8.5),
    "Turbidity": (0, 5),
    "Dissolved Oxygen": (5, 14),
    "Nitrate": (0, 10)
}

# Load data if the file exists
if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
    data = pd.read_csv(file_path)

    if "Zipcode" in data.columns:
        # Convert relevant columns to numeric
        for col in ["pH", "Turbidity", "Dissolved Oxygen", "Nitrate"]:
            data[col] = pd.to_numeric(data[col], errors="coerce")

        # Calculate average values for each parameter by Zipcode
        latest_data = data.groupby("Zipcode").mean(numeric_only=True).reset_index()

        # Display a simplified health-focused analysis
        st.header("Water Quality in Your Area")
        for index, row in latest_data.iterrows():
            st.subheader(f"Zipcode: {row['Zipcode']}")
            st.write("Here’s a quick overview of water quality in your area.")

            # Display info and health relevance for each parameter
            for param, info in learning_info.items():
                st.write(f"### {info['icon']} {param} - {info['importance']}")
                st.write(f"**Why It Matters:** {info['health_effects']}")
                
                # Display ideal range
                st.write(f"**Ideal Range:** {info['ideal_range']}")

                # Show current data for the parameter with visual indicators
                current_value = row[param]
                if pd.notna(current_value):
                    # Interpret if value is within safe range
                    in_safe_range = safe_ranges[param][0] <= current_value <= safe_ranges[param][1]
                    status = "Safe" if in_safe_range else "Alert"

                    # Display with colored badge and progress bar
                    color = "green" if in_safe_range else "red"
                    st.write(f"- **Current Level**: {current_value:.2f} ({status})", 
                             unsafe_allow_html=True)

                    # Progress bar to visualize parameter relative to safe range
                    safe_min, safe_max = safe_ranges[param]
                    max_display = max(safe_max, current_value)
                    st.progress(min(current_value / max_display, 1.0))

                    # Show tips if out of range
                    if not in_safe_range:
                        st.warning(f"Tip: {info['tips']}")
                else:
                    st.write(f"- **Current Level**: No data available")

            # Overall water quality assessment
            st.write("### General Water Safety")
            if all([safe_ranges["pH"][0] <= row["pH"] <= safe_ranges["pH"][1],
                    row["Turbidity"] <= safe_ranges["Turbidity"][1],
                    safe_ranges["Dissolved Oxygen"][0] <= row["Dissolved Oxygen"] <= safe_ranges["Dissolved Oxygen"][1],
                    row["Nitrate"] <= safe_ranges["Nitrate"][1]]):
                st.success("✅ All parameters in this area are within safe levels!")
            else:
                st.error("⚠️ Some parameters are out of range. Please check each above for guidance.")
    else:
        st.error("The data file is missing the 'Zipcode' column. Please check the data format.")
else:
    st.warning("No data available for analysis. Please submit data on the input page.")

# Footer with Additional Links
st.markdown("---")
st.write("Developed by Orange Team | Powered by [Streamlit](https://streamlit.io/) and [OpenAI](https://openai.com)")
st.write("For inquiries, contact jhetkenneth.advincula@sjsu.edu (mailto:your.email@company.com)")