import streamlit as st
import pandas as pd
from .data_manager import load_json_data, TRACK_BOOSTS_FILE, BOOSTS_FILE, SERIES_SETUPS_FILE
from .utils import safe_float, safe_int

def standardize_track(track_dict):
    """Ensure track dict has consistent keys and types"""
    # Create a copy to avoid modifying the original
    track = track_dict.copy()
    
    # Ensure all required fields exist
    if 'primary_attribute' not in track:
        track['primary_attribute'] = ""
    
    if 'focus' not in track:
        track['focus'] = ""
    
    if 'boosts' not in track:
        track['boosts'] = []
    
    return track

def get_track_groups(track_name, boosts):
    """Find all track groups that contain the specified track"""
    track_groups = []
    
    for boost in boosts:
        if "track_groups" in boost:
            for group in boost["track_groups"]:
                if track_name in group and group not in track_groups:
                    track_groups.append(group)
    
    return track_groups

def manage_tracks():
    """Function to manage tracks and their boost recommendations"""
    st.header("Track & Boost Management")
    
    # Load track and boost data
    tracks_data = load_json_data(TRACK_BOOSTS_FILE)
    boosts_data = load_json_data(BOOSTS_FILE)
    
    if not tracks_data or not boosts_data:
        st.error("Failed to load track or boost data")
        return
    
    # Extract data
    tracks = tracks_data.get("tracks", [])
    boosts = boosts_data.get("boosts", [])
    
    # Standardize all tracks
    tracks = [standardize_track(track) for track in tracks]
    
    # Create track dataframe
    try:
        tracks_df = pd.DataFrame([{
            "Name": t["name"],
            "Primary Attribute": t["primary_attribute"],
            "Focus": t["focus"],
            "Recommended Boosts": len(t.get("boosts", []))
        } for t in tracks])
    except Exception as e:
        st.error(f"Error creating tracks dataframe: {e}")
        st.exception(e)
        return
    
    # Add filters in sidebar
    st.sidebar.subheader("Track Filters")
    
    attributes = ["All"] + sorted(tracks_df["Primary Attribute"].unique().tolist())
    selected_attribute = st.sidebar.selectbox("Filter by Attribute", attributes)
    
    focus_areas = ["All"] + sorted(tracks_df["Focus"].unique().tolist())
    selected_focus = st.sidebar.selectbox("Filter by Focus Area", focus_areas)
    
    # Apply filters
    filtered_df = tracks_df.copy()
    if selected_attribute != "All":
        filtered_df = filtered_df[filtered_df["Primary Attribute"] == selected_attribute]
    if selected_focus != "All":
        filtered_df = filtered_df[filtered_df["Focus"] == selected_focus]
    
    # Display filtered tracks
    st.subheader(f"Tracks ({len(filtered_df)} of {len(tracks_df)})")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    
    # Track selection for details
    st.subheader("Track Details & Recommended Boosts")
    
    # Get track names
    track_names = filtered_df["Name"].tolist()
    
    if not track_names:
        st.warning("No tracks match the current filters")
        return
    
    selected_track_name = st.selectbox("Select track", track_names)
    
    # Find the selected track
    selected_track = next((t for t in tracks if t["name"] == selected_track_name), None)
    
    if selected_track:
        # Create columns for details and boosts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Primary Attribute:** {selected_track['primary_attribute']}")
            st.markdown(f"**Focus Area:** {selected_track['focus']}")
        
        with col2:
            # Get track groups
            track_groups = get_track_groups(selected_track_name, boosts)
            
            if track_groups:
                st.markdown(f"**Track Groups:** {', '.join(track_groups)}")
        
        # Display recommended boosts
        st.subheader("Recommended Boosts")
        
        track_boosts = selected_track.get("boosts", [])
        
        if track_boosts:
            try:
                boost_df = pd.DataFrame([{
                    "Boost": b["name"],
                    "Primary Stat": selected_track['primary_attribute'],
                    "Primary Value": safe_float(b.get("stats", {}).get(selected_track['primary_attribute'].lower().replace(" ", "_"), 0)),
                    "Focus Stat": selected_track['focus'],
                    "Focus Value": safe_float(b.get("stats", {}).get(selected_track['focus'].lower().replace(" ", "_"), 0)),
                    "Final Stat": b.get("final_stat", ""),
                    "Final Value": safe_float(b.get("final_value", 0))
                } for b in track_boosts])
                
                st.dataframe(boost_df, use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"Error creating boost dataframe: {e}")
                st.exception(e)
        else:
            st.info("No recommended boosts for this track")

def manage_series_setups():
    """Function to manage series setup recommendations"""
    st.header("Series Setup Management")
    
    # Load series setup data
    data = load_json_data(SERIES_SETUPS_FILE)
    
    if not data:
        st.error("Failed to load series setup data")
        return
    
    series_setups = data.get("series_setups", [])
    
    # Create sidebar selection for series
    st.sidebar.subheader("Series Selection")
    series_numbers = [safe_int(s["series"]) for s in series_setups]
    selected_series = st.sidebar.selectbox("Select Series", series_numbers)
    
    # Find selected series
    selected_setup = next((s for s in series_setups if safe_int(s["series"]) == selected_series), None)
    
    if not selected_setup:
        st.warning(f"No setup data found for Series {selected_series}")
        return
    
    # Display series setup
    st.subheader(f"Series {selected_series} Setups")
    
    # Create tabs for different focus areas
    tab1, tab2, tab3 = st.tabs(["Speed", "Cornering", "Power Unit"])
    
    # Helper function to display setup
    def display_setup(setup, focus):
        try:
            df = pd.DataFrame([{
                "Component": s["component"],
                "Value": safe_float(s["value"])  # Ensure values are treated as floats
            } for s in setup])
            
            if not df.empty:
                # Sort by value (descending)
                df = df.sort_values(by="Value", ascending=False)
                
                # Add a bar chart
                st.bar_chart(data=df.set_index("Component"), use_container_width=True)
                
                # Show the data table with all components
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Add a total value display
                total_value = df["Value"].sum()
                st.info(f"Total {focus} Value: {total_value:.1f}")
            else:
                st.info(f"No {focus} setup data for Series {selected_series}")
        except Exception as e:
            st.error(f"Error displaying {focus} setup: {e}")
            st.exception(e)
    
    # Display each focus area
    with tab1:
        display_setup(selected_setup["setups"].get("speed", []), "Speed")
    
    with tab2:
        display_setup(selected_setup["setups"].get("cornering", []), "Cornering")
    
    with tab3:
        display_setup(selected_setup["setups"].get("power_unit", []), "Power Unit") 