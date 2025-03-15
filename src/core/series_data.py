import pandas as pd
import os
import json
import streamlit as st
from src.utils.utils import safe_int, safe_float
from src.utils.config import config, LOADOUTS_FILE

# Path for the series data file
SERIES_DATA_FILE = "series_data.json"

# Default series information if the data file doesn't exist
DEFAULT_SERIES_DATA = [
    {"series": 1, "track_stats": "Defending", "recommended_ts": "0 - 350"},
    {"series": 2, "track_stats": "Tyre Mgmt", "recommended_ts": "250 - 450"},
    {"series": 3, "track_stats": "Speed", "recommended_ts": "350 - 600"},
    {"series": 4, "track_stats": "Overtaking", "recommended_ts": "450 - 700"},
    {"series": 5, "track_stats": "Cornering", "recommended_ts": "550 - 800"},
    {"series": 6, "track_stats": "Race Start", "recommended_ts": "650 - 900"},
    {"series": 7, "track_stats": "Power Unit", "recommended_ts": "750 - 1000"},
    {"series": 8, "track_stats": "Defending", "recommended_ts": "850 - 1100"},
    {"series": 9, "track_stats": "Speed", "recommended_ts": "950 - 1200"},
    {"series": 10, "track_stats": "Rotating", "recommended_ts": "1050 - 1300"},
    {"series": 11, "track_stats": "Rotating", "recommended_ts": "1250 - 1550"},
    {"series": 12, "track_stats": "Rotating", "recommended_ts": "1450 - 1799"},
]

# Add Grand Prix as a special series
DEFAULT_SERIES_DATA.append({"series": 0, "track_stats": "Custom", "recommended_ts": "1000+"})

# Map of track stats to loadout attributes - helps match loadouts to series
TRACK_STATS_TO_ATTRIBUTES = {
    "Defending": "defending",
    "Tyre Mgmt": "tyre_mgmt",
    "Speed": "speed",
    "Overtaking": "overtaking",
    "Cornering": "cornering",
    "Race Start": "race_start",
    "Power Unit": "power_unit",
    "Custom": "custom"  # For Grand Prix
}

# Path for storing current rotating series attributes
ROTATING_SERIES_FILE = "rotating_series.json"

def get_series_data():
    """Get series data from file or return default"""
    try:
        if os.path.exists(SERIES_DATA_FILE):
            with open(SERIES_DATA_FILE, 'r') as f:
                data = json.load(f)
                if "series_data" in data and isinstance(data["series_data"], list):
                    return data["series_data"]
        return DEFAULT_SERIES_DATA
    except Exception as e:
        st.warning(f"Error loading series data, using defaults: {e}")
        return DEFAULT_SERIES_DATA

# Initialize series data from file
SERIES_DATA = get_series_data()

def load_series_data_from_csv(file_path):
    """Load series data from the CSV file"""
    try:
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            series_data = []
            for _, row in df.iterrows():
                series_data.append({
                    "series": safe_int(row["Series"]),
                    "track_stats": row["Track Stats"],
                    "recommended_ts": row["Recommend TS"]
                })
            return series_data
        return SERIES_DATA
    except Exception as e:
        st.error(f"Error loading series data from CSV: {e}")
        return SERIES_DATA

def get_rotating_series_attributes():
    """Get the current attributes for the rotating series"""
    try:
        if os.path.exists(ROTATING_SERIES_FILE):
            with open(ROTATING_SERIES_FILE, 'r') as f:
                return json.load(f)
        else:
            # Default values
            return {
                "10": "Speed",
                "11": "Cornering",
                "12": "Power Unit"
            }
    except Exception as e:
        st.warning(f"Could not load rotating series attributes: {e}")
        return {
            "10": "Speed",
            "11": "Cornering",
            "12": "Power Unit"
        }

def save_rotating_series_attributes(attributes):
    """Save the current attributes for the rotating series"""
    try:
        with open(ROTATING_SERIES_FILE, 'w') as f:
            json.dump(attributes, f)
        return True
    except Exception as e:
        st.error(f"Error saving rotating series attributes: {e}")
        return False

def find_best_loadouts_for_series(series_number, loadouts, rotating_attributes=None):
    """Find the best loadouts for a given series based on track stats"""
    series_info = next((s for s in SERIES_DATA if s["series"] == series_number), None)
    
    if not series_info:
        return []
    
    track_stats = series_info["track_stats"]
    
    # Handle rotating series
    if track_stats == "Rotating" and rotating_attributes and str(series_number) in rotating_attributes:
        track_stats = rotating_attributes[str(series_number)]
    
    # Get the attribute to focus on
    focus_attribute = TRACK_STATS_TO_ATTRIBUTES.get(track_stats, "speed")  # Default to speed if not found
    
    # Calculate loadout scores based on the focus attribute
    loadout_scores = []
    for loadout in loadouts:
        score = 0
        
        # Safe access to calculations and stats
        calculations = loadout.get("calculations", {})
        car_stats = calculations.get("car_stats", {})
        driver_stats = calculations.get("driver_stats", {})
        total_value = calculations.get("total_value", 0)
        
        # Score from car stats
        if focus_attribute in ["speed", "cornering", "power_unit", "qualifying"]:
            score += car_stats.get(focus_attribute, 0) * 2  # Double weight for car stats
        elif focus_attribute == "pit_time":
            # For pit time, lower is better, so invert the score
            pit_time = car_stats.get("pit_time", 5.0)
            score += (5.0 - pit_time) * 20  # Scale to make it comparable
        
        # Score from driver stats
        if focus_attribute in ["overtaking", "defending", "qualifying"]:
            score += driver_stats.get(focus_attribute, 0)
        elif focus_attribute == "race_start":
            score += driver_stats.get("race_start", driver_stats.get("raceStart", 0))
        elif focus_attribute == "tyre_mgmt":
            score += driver_stats.get("tyre_mgmt", driver_stats.get("tyreMgmt", 0))
        
        # Add a bonus for total value
        score += total_value * 0.1  # Small weight for total value
        
        # Check recommended TS range
        ts_range = series_info["recommended_ts"].split(" - ")
        min_ts = safe_int(ts_range[0]) if len(ts_range) > 0 else 0
        max_ts = safe_int(ts_range[1]) if len(ts_range) > 1 else 9999
        
        if total_value < min_ts:
            score -= (min_ts - total_value) * 0.5  # Penalty for being under min TS
        elif total_value > max_ts:
            score -= (total_value - max_ts) * 0.2  # Smaller penalty for being over max TS
        
        loadout_scores.append({
            "loadout": loadout,
            "score": score
        })
    
    # Sort by score (descending)
    loadout_scores.sort(key=lambda x: x["score"], reverse=True)
    
    # Return the loadouts with their scores
    return loadout_scores

def manage_series_loadouts():
    """Function to manage and recommend loadouts by series"""
    st.header("Series Loadouts Manager")
    st.write("Manage and view loadouts organized by series")
    
    # Load loadouts data
    loadouts_data = config.load_json_data(LOADOUTS_FILE)
    if not loadouts_data:
        st.error("Failed to load loadouts data.")
        return
    
    loadouts = loadouts_data.get("loadouts", [])
    
    if not loadouts:
        st.warning("No loadouts available. Please create loadouts first.")
        return
    
    # Get rotating series attributes
    rotating_attributes = get_rotating_series_attributes()
    
    # Create tabs for different series categories
    tab_grand_prix, tab_series_8, tab_series_9, tab_series_10 = st.tabs([
        "Grand Prix", "Series 8", "Series 9", "Series 10+"
    ])
    
    with tab_grand_prix:
        _display_series_loadouts(0, loadouts, rotating_attributes)
    
    with tab_series_8:
        _display_series_loadouts(8, loadouts, rotating_attributes)
    
    with tab_series_9:
        _display_series_loadouts(9, loadouts, rotating_attributes)
    
    with tab_series_10:
        # For Series 10+, we need a way to set the current track stats
        st.subheader("Rotating Series")
        st.write("These series have rotating track stats. Set the current dominant stat for each series:")
        
        # Create columns for the three rotating series
        col1, col2, col3 = st.columns(3)
        
        with col1:
            rotating_attributes["10"] = st.selectbox(
                "Series 10 Current Stat",
                ["Speed", "Cornering", "Power Unit", "Defending", "Overtaking", "Race Start", "Tyre Mgmt"],
                index=["Speed", "Cornering", "Power Unit", "Defending", "Overtaking", "Race Start", "Tyre Mgmt"].index(rotating_attributes.get("10", "Speed"))
            )
            _display_series_loadouts(10, loadouts, rotating_attributes)
        
        with col2:
            rotating_attributes["11"] = st.selectbox(
                "Series 11 Current Stat",
                ["Speed", "Cornering", "Power Unit", "Defending", "Overtaking", "Race Start", "Tyre Mgmt"],
                index=["Speed", "Cornering", "Power Unit", "Defending", "Overtaking", "Race Start", "Tyre Mgmt"].index(rotating_attributes.get("11", "Cornering"))
            )
            _display_series_loadouts(11, loadouts, rotating_attributes)
        
        with col3:
            rotating_attributes["12"] = st.selectbox(
                "Series 12 Current Stat",
                ["Speed", "Cornering", "Power Unit", "Defending", "Overtaking", "Race Start", "Tyre Mgmt"],
                index=["Speed", "Cornering", "Power Unit", "Defending", "Overtaking", "Race Start", "Tyre Mgmt"].index(rotating_attributes.get("12", "Power Unit"))
            )
            _display_series_loadouts(12, loadouts, rotating_attributes)
        
        # Save the rotating attributes
        if st.button("Save Rotating Series Settings"):
            if save_rotating_series_attributes(rotating_attributes):
                st.success("Saved rotating series settings!")
            else:
                st.error("Failed to save rotating series settings.")

def _display_series_loadouts(series_number, loadouts, rotating_attributes):
    """Helper function to display loadout recommendations for a specific series"""
    # Get series info
    series_info = next((s for s in SERIES_DATA if s["series"] == series_number), None)
    
    if not series_info:
        st.error(f"Series {series_number} information not found.")
        return
    
    # Display series info
    track_stats = series_info["track_stats"]
    if track_stats == "Rotating" and rotating_attributes and str(series_number) in rotating_attributes:
        track_stats = rotating_attributes[str(series_number)]
    
    if series_number == 0:
        st.subheader("Grand Prix Loadouts")
        st.write("Recommended loadouts for Grand Prix events")
    else:
        st.subheader(f"Series {series_number} Loadouts")
        st.write(f"Recommended loadouts for Series {series_number} - Focus: **{track_stats}**")
    
    # Find best loadouts for this series
    best_loadouts = find_best_loadouts_for_series(series_number, loadouts, rotating_attributes)
    
    if not best_loadouts:
        st.info(f"No suitable loadouts found for Series {series_number}.")
        return
    
    # Display top 3 recommended loadouts
    top_loadouts = best_loadouts[:3]
    
    cols = st.columns(len(top_loadouts))
    
    for i, loadout_score in enumerate(top_loadouts):
        loadout = loadout_score["loadout"]
        with cols[i]:
            # Ensure we have an ID
            loadout_id = loadout.get('id', i+1)
            
            st.markdown(f"### {i+1}. {loadout['title']}")
            
            # Display main stats
            stats = []
            calculations = loadout.get("calculations", {})
            car_stats = calculations.get("car_stats", {})
            driver_stats = calculations.get("driver_stats", {})
            total_value = calculations.get("total_value", 0)
            
            # Display key stats based on the series focus
            focus_attribute = TRACK_STATS_TO_ATTRIBUTES.get(track_stats, "speed")
            if focus_attribute in ["speed", "cornering", "power_unit", "qualifying"]:
                stats.append(f"**{track_stats}**: {car_stats.get(focus_attribute, 0):.1f}")
            elif focus_attribute == "pit_time":
                stats.append(f"**Pit Time**: {car_stats.get('pit_time', 0):.2f}s")
            elif focus_attribute in ["overtaking", "defending", "race_start", "tyre_mgmt"]:
                # Convert to display format
                display_name = focus_attribute.replace("_", " ").title()
                
                # Handle different key formats
                if focus_attribute == "race_start":
                    value = driver_stats.get("race_start", driver_stats.get("raceStart", 0))
                elif focus_attribute == "tyre_mgmt":
                    value = driver_stats.get("tyre_mgmt", driver_stats.get("tyreMgmt", 0))
                else:
                    value = driver_stats.get(focus_attribute, 0)
                    
                stats.append(f"**{display_name}**: {value}")
            
            # Always show total value
            stats.append(f"**Total Value**: {total_value:.1f}")
            
            st.markdown(" | ".join(stats))
            
            # Create a more reliable view button with a unique key
            button_key = f"view_series_{series_number}_loadout_{loadout_id}_{i}"
            if st.button(f"View Loadout Details", key=button_key):
                # Store the loadout ID in session state
                if 'view_loadout' not in st.session_state:
                    st.session_state['view_loadout'] = loadout_id
                else:
                    st.session_state.view_loadout = loadout_id
                    
                # Set the page to Loadouts Manager
                if 'page' not in st.session_state:
                    st.session_state['page'] = "Loadouts Manager"
                else:
                    st.session_state.page = "Loadouts Manager"
                
                # Add a flag to indicate navigation from series loadouts
                st.session_state['from_series_view'] = True
                
                # Trigger a rerun to navigate
                st.rerun() 