import json
import streamlit as st
import os

# Define file paths
DRIVERS_FILE = "drivers.json"
COMPONENT_FILES = {
    "Brakes": "components_brakes.json",
    "Gearbox": "components_gearbox.json",
    "Rear Wing": "components_rearwing.json",
    "Front Wing": "components_frontwing.json",
    "Suspension": "components_suspension.json",
    "Engine": "components_engine.json"
}
# Add new file paths for track-related data
TRACK_BOOSTS_FILE = "track_boosts.json"
SERIES_SETUPS_FILE = "series_setups.json"
BOOSTS_FILE = "boosts.json"
# Add new file path for loadouts
LOADOUTS_FILE = "loadouts.json"

def load_json_data(file_path):
    """Load data from a JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading data from {file_path}: {e}")
        return None

def save_json_data(data, file_path):
    """Save data to a JSON file"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving data to {file_path}: {e}")
        return False 