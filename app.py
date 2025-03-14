import streamlit as st
import pandas as pd
import json
import os
from modules.data_manager import DRIVERS_FILE, COMPONENT_FILES, TRACK_BOOSTS_FILE, SERIES_SETUPS_FILE, BOOSTS_FILE, LOADOUTS_FILE
from modules.loadouts import manage_loadouts
from modules.drivers import manage_drivers
from modules.components import manage_components
from modules.tracks import manage_tracks, manage_series_setups
from modules.import_tools import import_special_csv_formats
from modules.series_data import manage_series_loadouts
from modules.grand_prix import manage_grand_prix
from ui.common import create_two_column_metrics

# Set page configuration
st.set_page_config(
    page_title="F1 Clash Data Manager",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main function to run the F1 Clash Manager application"""
    
    # Create sidebar for navigation
    st.sidebar.title("F1 Clash Manager")
    
    # Define navigation options
    nav_options = [
        "Home",
        "Loadouts Manager",
        "Series Loadouts",
        "Grand Prix Manager",
        "Drivers Manager",
        "Components Manager",
        "Tracks Manager",
        "Series Setups",
        "Import Tools"
    ]
    
    # Get current page from session state or use radio button
    if 'page' in st.session_state:
        selected_page = st.session_state.page
        # Find the index of this page in nav_options
        page_index = nav_options.index(selected_page) if selected_page in nav_options else 0
    else:
        page_index = 0
    
    # Create navigation sidebar with the current page pre-selected
    selected_page = st.sidebar.radio("Navigation", nav_options, index=page_index)
    
    # Update the session state if the page changed via the radio button
    if 'page' not in st.session_state or st.session_state.page != selected_page:
        st.session_state.page = selected_page
    
    # Display the selected page
    try:
        if selected_page == "Home":
            display_home_page()
        elif selected_page == "Loadouts Manager":
            manage_loadouts()
        elif selected_page == "Series Loadouts":
            manage_series_loadouts()
        elif selected_page == "Grand Prix Manager":
            manage_grand_prix()
        elif selected_page == "Drivers Manager":
            manage_drivers()
        elif selected_page == "Components Manager":
            display_components_page()
        elif selected_page == "Tracks Manager":
            manage_tracks()
        elif selected_page == "Series Setups":
            manage_series_setups()
        elif selected_page == "Import Tools":
            import_special_csv_formats()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.exception(e)
    
    # Add footer
    st.sidebar.markdown("---")
    st.sidebar.info("F1 Clash Manager v2.0")
    st.sidebar.markdown("Made with ❤️ for F1 Clash players")

def display_home_page():
    """Display the home page with application information and statistics"""
    st.title("F1 Clash Manager")
    st.write("Welcome to the F1 Clash Manager - a tool to help you manage your F1 Clash game data.")
    
    # Add information about the application
    st.markdown("""
    ## Features
    - **Loadouts Manager**: Create, edit, and compare car and driver loadouts
    - **Series Loadouts**: Organize loadouts by series and get series-specific recommendations
    - **Grand Prix Manager**: Plan your Grand Prix events with category-specific loadouts
    - **Drivers Manager**: Manage driver data and statistics
    - **Components Manager**: Manage car components and their stats
    - **Tracks Manager**: View track information and recommended setups
    - **Series Setups**: View recommended setups for each series
    - **Import Tools**: Import data from spreadsheets and other sources
    
    ## How to Use
    Use the navigation sidebar on the left to access different features of the application.
    """)
    
    # Add some statistics about the current data
    st.subheader("Current Data Statistics")
    
    # Create columns for stats
    col1, col2 = st.columns(2)
    
    try:
        stats = {}
        
        # Count loadouts
        if os.path.exists(LOADOUTS_FILE):
            with open(LOADOUTS_FILE, 'r') as f:
                loadouts_data = json.load(f)
                stats["Loadouts"] = len(loadouts_data.get("loadouts", []))
        else:
            stats["Loadouts"] = 0
        
        # Count drivers
        if os.path.exists(DRIVERS_FILE):
            with open(DRIVERS_FILE, 'r') as f:
                drivers_data = json.load(f)
                drivers = drivers_data.get("drivers", [])
                stats["Total Drivers"] = len(drivers)
                stats["Owned Drivers"] = sum(1 for d in drivers if d.get("inInventory", False))
        else:
            stats["Total Drivers"] = 0
            stats["Owned Drivers"] = 0
        
        # Count components
        total_components = 0
        owned_components = 0
        
        for component_type, file_path in COMPONENT_FILES.items():
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    component_data = json.load(f)
                    key = component_type.lower().replace(" ", "_")
                    components = component_data.get(key, [])
                    total_components += len(components)
                    owned_components += sum(1 for c in components if c.get("inInventory", False))
        
        stats["Total Components"] = total_components
        stats["Owned Components"] = owned_components
        
        # Count tracks
        if os.path.exists(TRACK_BOOSTS_FILE):
            with open(TRACK_BOOSTS_FILE, 'r') as f:
                tracks_data = json.load(f)
                stats["Tracks"] = len(tracks_data.get("tracks", []))
        else:
            stats["Tracks"] = 0
        
        # Display stats
        with col1:
            create_two_column_metrics({
                "Loadouts": stats["Loadouts"],
                "Total Drivers": stats["Total Drivers"],
                "Owned Drivers": stats["Owned Drivers"]
            })
        
        with col2:
            create_two_column_metrics({
                "Total Components": stats["Total Components"],
                "Owned Components": stats["Owned Components"],
                "Tracks": stats["Tracks"]
            })
        
    except Exception as e:
        st.warning(f"Could not read all data files. Some statistics may be missing. Error: {str(e)}")
    
    # Add a section for quick links
    st.subheader("Quick Links")
    
    quick_links_col1, quick_links_col2, quick_links_col3, quick_links_col4 = st.columns(4)
    
    with quick_links_col1:
        if st.button("Manage Loadouts", use_container_width=True, key="home_loadouts_btn"):
            st.session_state.page = "Loadouts Manager"
            st.rerun()
    
    with quick_links_col2:
        if st.button("Series Loadouts", use_container_width=True, key="home_series_btn"):
            st.session_state.page = "Series Loadouts"
            st.rerun()
    
    with quick_links_col3:
        if st.button("Grand Prix Manager", use_container_width=True, key="home_gp_btn"):
            st.session_state.page = "Grand Prix Manager"
            st.rerun()
    
    with quick_links_col4:
        if st.button("Manage Drivers", use_container_width=True, key="home_drivers_btn"):
            st.session_state.page = "Drivers Manager"
            st.rerun()

def display_components_page():
    """Display the components page with component type selection"""
    st.header("Components Manager")
    
    # Create component type selection
    component_types = list(COMPONENT_FILES.keys())
    selected_type = st.selectbox("Select Component Type", component_types)
    
    # Call the component management function with the selected type
    manage_components(selected_type)

if __name__ == "__main__":
    main() 