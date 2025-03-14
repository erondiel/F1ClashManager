import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from .data_manager import load_json_data, save_json_data, LOADOUTS_FILE, DRIVERS_FILE, COMPONENT_FILES
from .utils import format_number, safe_float, safe_int, get_current_timestamp
from .series_data import SERIES_DATA, find_best_loadouts_for_series
from .loadouts import find_matching_series_for_loadout

# Path for Grand Prix data
GP_EVENTS_FILE = "gp_events.json"
GP_LOADOUTS_FILE = "grand_prix_loadouts.json"

# Define Grand Prix categories and their series limitations
GP_CATEGORIES = {
    "Challenger": {"max_series": 6, "description": "Components and drivers from series 6 and below"},
    "Contender": {"max_series": 9, "description": "Components and drivers from series 9 and below"},
    "Champion": {"max_series": 12, "description": "No limitations on components and drivers"}
}

# Define Grand Prix race types
GP_RACE_TYPES = ["Qualifying", "Opening", "Final"]

# Define number of races for each type
GP_RACE_COUNTS = {
    "Qualifying": 4,
    "Opening": 8,
    "Final": 8
}

def get_data_directory():
    """Get the directory for data files"""
    # Try to use the same directory as other data files
    try:
        from .data_manager import get_data_directory as get_dm_directory
        return get_dm_directory()
    except (ImportError, AttributeError):
        # Fallback to current directory if data_manager function not available
        return os.path.join(os.getcwd(), "data")

def save_gp_events(events):
    """Save GP events to JSON file"""
    filename = "gp_events.json"
    file_path = os.path.join(get_data_directory(), filename)
    
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as file:
            json.dump(events, file, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving GP events: {str(e)}")
        return False

def load_gp_events():
    """Load GP events from JSON file or initialize if not exists"""
    filename = "gp_events.json"
    file_path = os.path.join(get_data_directory(), filename)
    
    # Initialize with empty events if file doesn't exist
    if not os.path.exists(file_path):
        events = []
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Create a default Australia GP event
        australia_event = create_australia_gp_event("australia_gp_1")
        events.append(australia_event)
        
        save_gp_events(events)
        return events
    
    try:
        with open(file_path, 'r') as file:
            events = json.load(file)
        
        # If there are no events, create a default Australia GP
        if not events:
            australia_event = create_australia_gp_event("australia_gp_1")
            events.append(australia_event)
            save_gp_events(events)
        
        # Fix any capitalization issues in existing events
        for event in events:
            if "races" in event:
                races = event["races"]
                
                # Check for lowercase keys and fix them
                lowercase_keys = [k for k in races.keys() if k in ["qualifying", "opening", "final"]]
                for key in lowercase_keys:
                    # Create properly capitalized key version
                    capitalized_key = key.capitalize()
                    if capitalized_key not in races:
                        races[capitalized_key] = races[key]
                    # Remove the lowercase key
                    races.pop(key, None)
                
        # Save any fixes we made
        save_gp_events(events)
        
        return events
    except (json.JSONDecodeError, FileNotFoundError):
        # Return empty list if file is corrupt or not found
        return []

def create_australia_gp_event(event_id):
    """Create the Australia GP event data"""
    return {
        "id": event_id,
        "name": "Australia Grand Prix",
        "category": "Challenger",
        "description": "F1 Clash Australia Event - March 2025",
        "date": "2025-03-15",
        "created_at": get_current_timestamp(),
        "races": {
            "Qualifying": [
                {"track": "Monaco", "lap_count": 8, "loadout_id": None}
                # Qualifying races already completed as mentioned
            ],
            "Opening": [
                {"track": "Melbourne", "lap_count": 8, "loadout_id": None},
                {"track": "Mexico City", "lap_count": 8, "loadout_id": None},
                {"track": "Barcelona", "lap_count": 9, "loadout_id": None},
                {"track": "Zandvoort", "lap_count": 8, "loadout_id": None},
                {"track": "Montreal", "lap_count": 8, "loadout_id": None},
                {"track": "Melbourne", "lap_count": 8, "loadout_id": None},
                {"track": "Singapore", "lap_count": 6, "loadout_id": None},
                {"track": "Suzuka", "lap_count": 7, "loadout_id": None},
            ],
            "Final": [
                {"track": "Melbourne", "lap_count": 8, "loadout_id": None},
                {"track": "Mexico City", "lap_count": 8, "loadout_id": None},
                {"track": "Barcelona", "lap_count": 9, "loadout_id": None},
                {"track": "Zandvoort", "lap_count": 8, "loadout_id": None},
                {"track": "Montreal", "lap_count": 8, "loadout_id": None},
                {"track": "Melbourne", "lap_count": 8, "loadout_id": None},
                {"track": "Singapore", "lap_count": 6, "loadout_id": None},
                {"track": "Suzuka", "lap_count": 7, "loadout_id": None},
            ]
        }
    }

def load_gp_loadouts():
    """Load Grand Prix loadouts data from file"""
    gp_loadouts_data = load_json_data(GP_LOADOUTS_FILE)
    if not gp_loadouts_data:
        # Create default structure if file doesn't exist
        gp_loadouts_data = {"grand_prix_loadouts": []}
        save_json_data(gp_loadouts_data, GP_LOADOUTS_FILE)
    return gp_loadouts_data

def get_component_series(component_name):
    """Get the series where a component is introduced"""
    for component_type, file_path in COMPONENT_FILES.items():
        components_data = load_json_data(file_path)
        if components_data:
            key = component_type.lower().replace(" ", "_")
            components = components_data.get(key, [])
            
            for component in components:
                if component.get("name") == component_name:
                    return component.get("series", 0)
    
    return 0  # Default to series 0 if component not found

def get_driver_series(driver_name):
    """Get the series where a driver is introduced"""
    drivers_data = load_json_data(DRIVERS_FILE)
    if drivers_data:
        drivers = drivers_data.get("drivers", [])
        
        for driver in drivers:
            if driver.get("name") == driver_name:
                return driver.get("series", 0)
    
    return 0  # Default to series 0 if driver not found

def is_loadout_valid_for_category(loadout, category):
    """Check if a loadout is valid for a GP category based on series limitations"""
    if category not in GP_CATEGORIES:
        return False
    
    max_series = GP_CATEGORIES[category]["max_series"]
    
    # More robust validation - check each component and driver
    # Check drivers
    for driver in loadout.get("drivers", []):
        if driver.get("name"):
            driver_series = get_driver_series(driver["name"])
            if driver_series > max_series:
                return False
    
    # Check components
    for comp_type, comp in loadout.get("components", {}).items():
        if comp.get("name"):
            comp_series = get_component_series(comp["name"])
            if comp_series > max_series:
                return False
    
    # If we passed all checks, the loadout is valid
    return True

def get_loadout_validation_message(loadout, category):
    """Get a validation message explaining why a loadout is invalid for a category"""
    if category not in GP_CATEGORIES:
        return f"Invalid category: {category}"
    
    max_series = GP_CATEGORIES[category]["max_series"]
    invalid_items = []
    
    # Check drivers
    for driver in loadout.get("drivers", []):
        if driver.get("name"):
            driver_series = get_driver_series(driver["name"])
            if driver_series > max_series:
                invalid_items.append(f"Driver '{driver['name']}' is from Series {driver_series}")
    
    # Check components
    for comp_type, comp in loadout.get("components", {}).items():
        if comp.get("name"):
            comp_series = get_component_series(comp["name"])
            if comp_series > max_series:
                invalid_items.append(f"{comp_type.title()} '{comp['name']}' is from Series {comp_series}")
    
    if invalid_items:
        return f"Loadout contains items above Series {max_series}:\n- " + "\n- ".join(invalid_items)
    
    return "Loadout is valid for this category"

def manage_grand_prix():
    """Main function to manage Grand Prix events and loadouts"""
    st.header("Grand Prix Manager")
    st.write("Manage your Grand Prix events and loadouts for specific tracks")
    
    # Create tabs for different GP management functions
    tab1, tab2 = st.tabs(["GP Events", "GP Loadouts"])
    
    with tab1:
        manage_gp_events()
    
    with tab2:
        manage_gp_loadouts()

def manage_gp_events():
    """Display Grand Prix events for visualization"""
    st.subheader("Grand Prix Events")
    
    # Load GP events data - now returns a list directly
    events = load_gp_events()
    
    # Refresh button
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Refresh Data", use_container_width=True):
            # Just trigger a rerun to refresh the data
            st.rerun()
    
    # Display existing events in a nice format
    if events:
        st.write("### Existing GP Events")
        
        # Create a DataFrame to display events
        events_data = []
        for event in events:
            events_data.append({
                "ID": event["id"],
                "Name": event["name"],
                "Category": event["category"],
                "Date": event["date"],
                "Races": f"Q: {len(event.get('races', {}).get('Qualifying', []))}, "
                        f"O: {len(event.get('races', {}).get('Opening', []))}, "
                        f"F: {len(event.get('races', {}).get('Final', []))}"
            })
        
        events_df = pd.DataFrame(events_data)
        st.dataframe(events_df, hide_index=True, use_container_width=True)
    
    # View event details (read-only)
    if events:
        st.write("### View Grand Prix Event Details")
        
        # Select existing event to view
        event_options = [f"{e['id']}. {e['name']}" for e in events]
        selected_event_option = st.selectbox("Select Event to View", event_options)
        
        # Extract ID without trying to convert to int
        event_id_str = selected_event_option.split(".")[0]
        selected_event = next((e for e in events if str(e["id"]) == event_id_str), None)
        
        if selected_event:
            st.write(f"## {selected_event['name']}")
            st.write(f"**Category:** {selected_event['category']}")
            st.write(f"**Date:** {selected_event['date']}")
            st.write(f"**Description:** {selected_event.get('description', 'No description')}")
            st.write(f"**Created:** {selected_event.get('created_at', 'Unknown')}")
            
            # Display race counts
            st.write("### Race Structure")
            race_structure = {
                "Qualifying Races": len(selected_event.get('races', {}).get('Qualifying', [])),
                "Opening Races": len(selected_event.get('races', {}).get('Opening', [])),
                "Final Races": len(selected_event.get('races', {}).get('Final', []))
            }
            
            structure_df = pd.DataFrame([race_structure])
            st.dataframe(structure_df, hide_index=True, use_container_width=True)
    else:
        st.info("No Grand Prix events available. Default events will be created automatically when needed.")

def manage_gp_loadouts():
    """Display Grand Prix loadouts for visualization"""
    st.subheader("Grand Prix Loadouts")
    
    # Add instruction box
    st.info("""
    ### GP Loadout Information
    
    This section displays loadouts specifically created for Grand Prix events.
    Loadouts are organized by category:
    
    - **Challenger**: Components and drivers from series 6 and below
    - **Contender**: Components and drivers from series 9 and below
    - **Champion**: No limitations on components and drivers
    
    Select a category tab below to view available loadouts.
    """)
    
    # Load GP loadouts
    gp_loadouts_data = load_gp_loadouts()
    gp_loadouts = gp_loadouts_data.get("grand_prix_loadouts", [])
    
    # Create tabs for different GP categories
    tab_challenger, tab_contender, tab_champion = st.tabs([
        f"Challenger (≤ S6)", 
        f"Contender (≤ S9)", 
        f"Champion (All)"
    ])
    
    with tab_challenger:
        display_category_loadouts("Challenger", gp_loadouts)
    
    with tab_contender:
        display_category_loadouts("Contender", gp_loadouts)
    
    with tab_champion:
        display_category_loadouts("Champion", gp_loadouts)

def display_category_loadouts(category, gp_loadouts):
    """Display loadouts for a specific GP category"""
    st.write(f"### {category} Loadouts")
    st.write(f"*{GP_CATEGORIES[category]['description']}*")
    
    # Filter GP loadouts for this category
    category_loadouts = [l for l in gp_loadouts if l.get("category") == category]
    
    # Display existing GP loadouts for this category
    if not category_loadouts:
        st.info(f"No {category} GP loadouts available.")
        return
    
    # Display in a tabular format
    loadouts_data = []
    for loadout in category_loadouts:
        calculations = loadout.get("calculations", {})
        car_stats = calculations.get("car_stats", {})
        focus = calculations.get("focus", {})
        
        # Get track info 
        tracks_info = ""
        if "tracks" in loadout and loadout["tracks"]:
            tracks_info = ", ".join(loadout["tracks"])
        elif "track" in loadout and loadout["track"]:
            tracks_info = loadout["track"]
            
        loadouts_data.append({
            "ID": loadout["id"],
            "Title": loadout["title"],
            "Tracks": tracks_info,
            "Focus": f"{focus.get('attribute', '')}/{focus.get('secondary', '')}",
            "Speed": car_stats.get("speed", 0),
            "Cornering": car_stats.get("cornering", 0),
            "Power Unit": car_stats.get("power_unit", 0),
            "Total Value": calculations.get("total_value", 0),
        })
    
    df = pd.DataFrame(loadouts_data)
    
    # Format numeric columns
    for col in ["Speed", "Cornering", "Power Unit", "Total Value"]:
        df[col] = df[col].apply(format_number)
    
    st.dataframe(df, hide_index=True, use_container_width=True)
    
    # Allow viewing a specific loadout
    selected_gp_loadout_id = st.selectbox(
        "Select a GP Loadout to View Details",
        [f"{l['id']}. {l['title']} - {', '.join(l.get('tracks', [l.get('track', '')]))} " for l in category_loadouts],
        key=f"view_gp_{category}"
    )
    
    # Extract ID without trying to convert to int
    loadout_id_str = selected_gp_loadout_id.split(".")[0]
    selected_gp_loadout = next((l for l in category_loadouts if str(l["id"]) == loadout_id_str), None)
    
    if selected_gp_loadout:
        st.write(f"### {selected_gp_loadout['title']}")
        
        # Display tracks prominently
        tracks_info = ""
        if "tracks" in selected_gp_loadout and selected_gp_loadout["tracks"]:
            tracks_info = ", ".join(selected_gp_loadout["tracks"])
        elif "track" in selected_gp_loadout and selected_gp_loadout["track"]:
            tracks_info = selected_gp_loadout["track"]
            
        if tracks_info:
            st.write(f"### 🏁 Tracks: {tracks_info}")
        
        # Show focus attributes prominently
        if "focus" in selected_gp_loadout["calculations"]:
            focus = selected_gp_loadout["calculations"]["focus"]
            st.write(f"**Focus Attributes:** Primary - {focus.get('attribute', 'None')}, Secondary - {focus.get('secondary', 'None')}")
        
        st.write(selected_gp_loadout.get('description', ''))
        st.write("---")
        
        # Display drivers and components
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("#### Drivers")
            for i, driver in enumerate(selected_gp_loadout["drivers"]):
                if driver["name"]:
                    positions = ", ".join(driver.get("positions", ["Driver"]))
                    st.write(f"Driver {i+1}: **{driver['name']}** ({driver['rarity']}, Level {driver['level']}) - *{positions}*")
        
        with col2:
            st.write("#### Components")
            for comp_type, comp in selected_gp_loadout["components"].items():
                if comp["name"]:
                    st.write(f"{comp_type.title()}: **{comp['name']}** (Level {comp['level']}, Series {comp['series']})")
        
        # Show stats
        st.write("#### Stats")
        car_stats = selected_gp_loadout["calculations"]["car_stats"]
        st.write(f"Speed: {format_number(car_stats['speed'])} | "
                 f"Cornering: {format_number(car_stats['cornering'])} | "
                 f"Power Unit: {format_number(car_stats['power_unit'])} | "
                 f"Total: {format_number(selected_gp_loadout['calculations']['total_value'])}")
        
        # Show matching series
        st.write("#### Best For Series")
        matching_series = find_matching_series_for_loadout(selected_gp_loadout)
        if matching_series:
            series_text = ", ".join([f"S{s['series']}" for s in matching_series[:3]])
            st.write(f"This loadout is best for: **{series_text}**")
            
        # Show race plan information
        events = load_gp_events()
        for event in events:
            if event.get("category") == category:
                st.write("#### Race Usage")
                st.write(f"Used in: **{event.get('name', 'Unknown Event')}**")
                
                # Count races using this loadout
                loadout_id = selected_gp_loadout["id"]
                race_counts = {}
                
                for race_type in GP_RACE_TYPES:
                    if race_type in event.get('races', {}):
                        races = event['races'][race_type]
                        count = sum(1 for race in races if str(race.get('loadout_id')) == str(loadout_id))
                        if count > 0:
                            race_counts[race_type] = count
                
                if race_counts:
                    race_usage = []
                    for race_type, count in race_counts.items():
                        race_usage.append(f"{count} {race_type} races")
                    
                    st.write(", ".join(race_usage)) 