import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from .data_manager import load_json_data, save_json_data, LOADOUTS_FILE, COMPONENT_FILES
from .utils import format_number, safe_float, safe_int, get_current_timestamp
from .series_data import SERIES_DATA, TRACK_STATS_TO_ATTRIBUTES, find_best_loadouts_for_series, get_rotating_series_attributes

def highlight_max(s, highlight_color='forestgreen'):
    """Highlight the maximum value in each column"""
    is_max = s == s.max()
    return [f"background-color: {highlight_color}; color: white" if v else '' for v in is_max]

def highlight_min(s, highlight_color='forestgreen'):
    """Highlight the minimum value in each column"""
    is_min = s == s.min()
    return [f"background-color: {highlight_color}; color: white" if v else '' for v in is_min]

def manage_loadouts():
    """
    Function to manage saved car and driver loadouts
    """
    st.header("F1 Clash Loadouts Manager")
    st.write("Create, edit, and manage your saved car and driver loadouts")
    
    # Check if we're navigating from the Series Loadouts section
    coming_from_series_view = st.session_state.get('from_series_view', False)
    if coming_from_series_view:
        # Clear the flag so it doesn't persist
        st.session_state['from_series_view'] = False
        # Add a breadcrumb navigation
        if st.button("← Back to Series Loadouts"):
            st.session_state.page = "Series Loadouts"
            st.rerun()
    
    # Load loadouts data
    loadouts_data = load_json_data(LOADOUTS_FILE)
    if not loadouts_data:
        st.error("Failed to load loadouts data.")
        return
    
    loadouts = loadouts_data.get("loadouts", [])
    
    # Add timestamps to loadouts if missing
    current_time = get_current_timestamp()
    for loadout in loadouts:
        if 'created_at' not in loadout:
            loadout['created_at'] = current_time
        if 'updated_at' not in loadout:
            loadout['updated_at'] = current_time
    
    # Create tabs for viewing and editing loadouts
    tab1, tab2, tab3 = st.tabs(["View Loadouts", "Compare Loadouts", "Series Match"])
    
    with tab1:
        st.subheader("Saved Loadouts")
        
        # Create a dropdown to select a loadout
        loadout_titles = [f"{l['id']}. {l['title']}" for l in loadouts]
        
        if not loadout_titles:
            st.info("No loadouts available. Create one in the 'Edit Loadout' tab.")
            return
        
        # Set the default selected loadout if coming from view_loadout session state
        default_index = 0
        if 'view_loadout' in st.session_state:
            view_loadout_id = st.session_state.view_loadout
            # Find the index of the loadout with this ID
            for idx, loadout in enumerate(loadouts):
                if loadout.get('id') == view_loadout_id:
                    default_index = idx
                    break
            # Clear the view_loadout from session state
            del st.session_state.view_loadout
        
        selected_loadout_index = st.selectbox(
            "Select a loadout to view", 
            range(len(loadout_titles)), 
            format_func=lambda x: loadout_titles[x],
            index=default_index
        )
        
        loadout = loadouts[selected_loadout_index]
        
        # Display loadout details
        st.markdown(f"### {loadout['title']}")
        
        # Show loadout metadata with safe access
        col1, col2, col3 = st.columns(3)
        with col1:
            created_at = loadout.get('created_at', 'Unknown')
            st.write(f"**Created:** {created_at}")
        with col2:
            updated_at = loadout.get('updated_at', 'Unknown')
            st.write(f"**Updated:** {updated_at}")
        with col3:
            # Find matching series for this loadout
            matching_series = find_matching_series_for_loadout(loadout)
            if matching_series:
                series_text = ", ".join([f"S{s['series']}" for s in matching_series[:3]])
                st.write(f"**Best For:** {series_text}")
                
                # Add a button to go to series loadouts
                if st.button("View in Series Loadouts"):
                    st.session_state.page = "Series Loadouts"
                    st.rerun()
        
        # Add a separator
        st.markdown("---")
        
        # Display the rest of the loadout information...
        
        # Add ability to edit the loadout title directly here
        col1, col2 = st.columns([3, 1])
        with col1:
            new_title = st.text_input("Edit Loadout Title", value=loadout['title'], key="view_title_input")
            if new_title != loadout['title']:
                loadout['title'] = new_title
                loadouts_data['loadouts'] = loadouts
                if save_json_data(loadouts_data, LOADOUTS_FILE):
                    st.success("Loadout title updated successfully!")
                else:
                    st.error("Failed to update loadout title.")
        
        with col2:
            # Add button to delete this loadout
            if st.button("Delete This Loadout"):
                loadouts.pop(selected_loadout_index)
                # Update IDs for remaining loadouts
                for i, ld in enumerate(loadouts, 1):
                    ld['id'] = i
                
                # Save updated loadouts
                loadouts_data['loadouts'] = loadouts
                if save_json_data(loadouts_data, LOADOUTS_FILE):
                    st.success("Loadout deleted successfully!")
                    st.rerun()
                else:
                    st.error("Failed to delete loadout.")
        
        # Display description if available - display in a more prominent way
        if 'description' in loadout and loadout['description']:
            # Split description into main part and track recommendations if they exist
            description_parts = loadout['description'].split('RECOMMENDED TRACKS:')
            if len(description_parts) > 1:
                # We have track recommendations
                main_desc = description_parts[0].strip()
                track_recs = description_parts[1].strip()
                
                # Display main description
                if main_desc:
                    st.info(f"Description: {main_desc}")
                
                # Display track recommendations in a more prominent box
                st.success(f"**RECOMMENDED TRACKS:** {track_recs}")
            else:
                # Just display the whole description
                st.info(f"Description: {loadout['description']}")
        
        # Display car stats
        st.markdown("### Car Stats")
        car_stats = loadout['calculations']['car_stats']
        car_stats_data = {
            "Stat": ["Speed", "Cornering", "Power Unit", "Qualifying", "Pit Time", "Total"],
            "Value": [
                format_number(car_stats['speed']),
                format_number(car_stats['cornering']),
                format_number(car_stats['power_unit']),
                format_number(car_stats['qualifying']),
                f"{car_stats['pit_time']:.2f}",
                format_number(car_stats['total_car_value'])
            ]
        }
        car_stats_df = pd.DataFrame(car_stats_data)
        st.dataframe(car_stats_df, use_container_width=True, hide_index=True)
        
        # Display components
        st.markdown("### Components")
        
        components_data = {
            "Component": [],
            "Name": [],
            "Level": [],
            "Speed": [],
            "Cornering": [],
            "Power Unit": [],
            "Qualifying": [],
            "Pit Time": []
        }
        
        for comp_type, comp_key in zip(COMPONENT_FILES.keys(), loadout['components'].keys()):
            component = loadout['components'][comp_key]
            if not component['name']:  # Skip empty components
                continue
                
            components_data["Component"].append(comp_type)
            components_data["Name"].append(component['name'])
            components_data["Level"].append(component['level'])
            components_data["Speed"].append(format_number(component['stats']['speed']))
            components_data["Cornering"].append(format_number(component['stats']['cornering']))
            components_data["Power Unit"].append(format_number(component['stats']['power_unit']))
            components_data["Qualifying"].append(format_number(component['stats']['qualifying']))
            components_data["Pit Time"].append(f"{component['stats']['pit_time']:.2f}")
        
        if components_data["Component"]:  # Only create dataframe if components exist
            components_df = pd.DataFrame(components_data)
            st.dataframe(components_df, use_container_width=True, hide_index=True)
        
        # Display driver stats
        st.markdown("### Driver Stats")
        driver_stats = loadout['calculations']['driver_stats']
        
        driver_stats_data = {
            "Stat": ["Overtaking", "Defending", "Qualifying", "Race Start", "Tyre Management", "Total"],
            "Driver 1": [0, 0, 0, 0, 0, 0],
            "Driver 2": [0, 0, 0, 0, 0, 0],
        }
        
        for i, driver in enumerate(loadout['drivers']):
            if not driver['name']:  # Skip empty drivers
                continue
                
            driver_col = f"Driver {i+1}"
            
            # Safely get race_start and tyre_mgmt with different possible key names
            race_start = driver['stats'].get('race_start', driver['stats'].get('raceStart', 0))
            tyre_mgmt = driver['stats'].get('tyre_mgmt', driver['stats'].get('tyreMgmt', 0))
            
            driver_stats_data[driver_col] = [
                driver['stats']['overtaking'],
                driver['stats']['defending'],
                driver['stats']['qualifying'],
                race_start,
                tyre_mgmt,
                sum([
                    driver['stats']['overtaking'],
                    driver['stats']['defending'],
                    driver['stats']['qualifying'],
                    race_start,
                    tyre_mgmt
                ])
            ]
            
        # Add driver names as headers
        driver_names = []
        for i, driver in enumerate(loadout['drivers']):
            if driver['name']:
                driver_names.append(f"{driver['name']} (Lvl {driver['level']})")
            else:
                driver_names.append(f"Driver {i+1}")
                
        if len(driver_names) >= 2:
            st.write(f"**{driver_names[0]}** and **{driver_names[1]}**")
                
        # Add combined stats column - handle both key formats with safe access
        driver_stats_data["Combined"] = [
            driver_stats.get('overtaking', 0),
            driver_stats.get('defending', 0),
            driver_stats.get('qualifying', 0),
            driver_stats.get('race_start', driver_stats.get('raceStart', 0)),
            driver_stats.get('tyre_mgmt', driver_stats.get('tyreMgmt', 0)),
            driver_stats.get('total_driver_value', 0)
        ]
        
        driver_stats_df = pd.DataFrame(driver_stats_data)
        st.dataframe(driver_stats_df, use_container_width=True, hide_index=True)
        
        st.info(f"Total Loadout Value: {format_number(loadout['calculations']['total_value'])}")
    
    with tab2:
        _display_loadouts_comparison(loadouts)
    
    with tab3:
        # Series Match tab
        display_series_match_tab(loadouts)

def _display_loadouts_comparison(loadouts):
    """Helper function to display the loadouts comparison tab"""
    st.subheader("Loadouts Comparison")
    st.write("Compare all your loadout setups side by side")
    
    # Create comparison dataframe
    comparison_data = []
    
    for loadout in loadouts:
        # Get car stats
        car_stats = loadout['calculations']['car_stats']
        
        # Create a row for each loadout
        comparison_data.append({
            "ID": int(loadout['id']),
            "Title": loadout['title'],
            "Speed": float(car_stats['speed']),
            "Cornering": float(car_stats['cornering']),
            "Power Unit": float(car_stats['power_unit']),
            "Qualifying": float(car_stats['qualifying']),
            "Pit Time": float(car_stats['pit_time']),
            "Total Value": float(loadout['calculations']['total_value'])
        })
    
    # Create and display dataframe
    if comparison_data:
        comparison_df = pd.DataFrame(comparison_data)
        
        # Create a display dataframe with formatted values for display
        display_df = pd.DataFrame({
            "ID": comparison_df["ID"],
            "Title": comparison_df["Title"],
            "Speed": [format_number(v) for v in comparison_df["Speed"]],
            "Cornering": [format_number(v) for v in comparison_df["Cornering"]],
            "Power Unit": [format_number(v) for v in comparison_df["Power Unit"]],
            "Qualifying": [format_number(v) for v in comparison_df["Qualifying"]],
            "Pit Time": [f"{v:.2f}" for v in comparison_df["Pit Time"]],
            "Total Value": [format_number(v) for v in comparison_df["Total Value"]]
        })
        
        # Use a darker green for better contrast with white text
        highlight_color = 'forestgreen'
        
        # Style the dataframe
        styled_df = display_df.style.apply(
            lambda x: highlight_max(comparison_df[x.name]) if x.name in ['Speed', 'Cornering', 'Power Unit', 'Qualifying', 'Total Value'] else '',
            axis=0,
            subset=['Speed', 'Cornering', 'Power Unit', 'Qualifying', 'Total Value']
        ).apply(
            lambda x: highlight_min(comparison_df[x.name]) if x.name == 'Pit Time' else '',
            axis=0,
            subset=['Pit Time']
        )
        
        # Display the styled dataframe
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        # Add visual comparison
        st.subheader("Visual Comparison")
        
        # Prepare data for Altair chart
        chart_data = []
        for _, row in comparison_df.iterrows():
            for stat in ['Speed', 'Cornering', 'Power Unit', 'Qualifying']:
                chart_data.append({
                    'Title': row['Title'],
                    'Stat': stat,
                    'Value': row[stat]
                })
        
        chart_df = pd.DataFrame(chart_data)
        
        # Create chart
        chart = alt.Chart(chart_df).mark_bar().encode(
            x=alt.X('Stat:N', title='Statistic'),
            y=alt.Y('Value:Q', title='Value'),
            color='Title:N',
            tooltip=['Title', 'Stat', 'Value']
        ).properties(
            height=400
        ).interactive()
        
        st.altair_chart(chart, use_container_width=True)

def find_matching_series_for_loadout(loadout):
    """Find which series this loadout is best suited for"""
    # Get rotating series attributes
    rotating_attributes = get_rotating_series_attributes()
    
    # Score this loadout for each series
    series_scores = []
    
    # Get calculations with safe default values
    calculations = loadout.get("calculations", {})
    car_stats = calculations.get("car_stats", {})
    driver_stats = calculations.get("driver_stats", {})
    total_value = calculations.get("total_value", 0)
    
    for series_info in SERIES_DATA:
        series_num = series_info["series"]
        
        # Skip Grand Prix (0) as it's special
        if series_num == 0:
            continue
        
        # Get track stats
        track_stats = series_info["track_stats"]
        
        # Handle rotating series
        if track_stats == "Rotating" and rotating_attributes and str(series_num) in rotating_attributes:
            track_stats = rotating_attributes[str(series_num)]
        
        # Get the focus attribute
        focus_attribute = TRACK_STATS_TO_ATTRIBUTES.get(track_stats, "speed")
        
        # Calculate score for this series
        score = 0
        
        # Score from car stats
        if focus_attribute in ["speed", "cornering", "power_unit", "qualifying"]:
            score += car_stats.get(focus_attribute, 0) * 2
        elif focus_attribute == "pit_time":
            pit_time = car_stats.get("pit_time", 5.0)
            score += (5.0 - pit_time) * 20
        
        # Score from driver stats
        if focus_attribute in ["overtaking", "defending", "qualifying", "race_start", "tyre_mgmt"]:
            # Handle both key formats for race_start and tyre_mgmt
            if focus_attribute == "race_start":
                value = driver_stats.get("race_start", driver_stats.get("raceStart", 0))
            elif focus_attribute == "tyre_mgmt":
                value = driver_stats.get("tyre_mgmt", driver_stats.get("tyreMgmt", 0))
            else:
                value = driver_stats.get(focus_attribute, 0)
            score += value
        
        # Add a bonus for total value
        score += total_value * 0.1
        
        # Check recommended TS range
        ts_range = series_info["recommended_ts"].split(" - ")
        min_ts = safe_int(ts_range[0]) if len(ts_range) > 0 else 0
        max_ts = safe_int(ts_range[1]) if len(ts_range) > 1 else 9999
        
        if total_value < min_ts:
            score -= (min_ts - total_value) * 0.5
        elif total_value > max_ts:
            score -= (total_value - max_ts) * 0.2
            
        # Add to our list
        series_scores.append({
            "series": series_num,
            "track_stats": track_stats,
            "score": score
        })
    
    # Sort by score (descending)
    series_scores.sort(key=lambda x: x["score"], reverse=True)
    
    # Return the top 5 matches
    return series_scores[:5]

def display_series_match_tab(loadouts):
    """Display the Series Match tab for analyzing which series a loadout is best for"""
    st.subheader("Match Loadouts to Series")
    st.write("Find which series your loadouts are best suited for.")
    
    if not loadouts:
        st.info("No loadouts available. Please create loadouts first.")
        return
    
    # Create a dropdown to select a loadout
    loadout_titles = [f"{l['id']}. {l['title']}" for l in loadouts]
    selected_loadout_index = st.selectbox(
        "Select a loadout to analyze",
        range(len(loadout_titles)),
        format_func=lambda x: loadout_titles[x],
        key="series_match_loadout_select"
    )
    
    loadout = loadouts[selected_loadout_index]
    
    # Find matching series
    matching_series = find_matching_series_for_loadout(loadout)
    
    # Display results
    st.markdown(f"### Best Series for '{loadout['title']}'")
    st.write("Based on the loadout's stats, these are the series it's best suited for:")
    
    # Create a dataframe for the results
    df = pd.DataFrame(matching_series)
    df = df.rename(columns={
        "series": "Series", 
        "track_stats": "Focus", 
        "score": "Match Score"
    })
    
    # Format the match score
    df["Match Score"] = df["Match Score"].map(lambda x: f"{x:.1f}")
    
    # Display the table
    st.table(df)
    
    # Add a button to go to series loadouts
    if st.button("Go to Series Loadouts"):
        st.session_state.page = "Series Loadouts"
        st.rerun() 