import streamlit as st
import json
import pandas as pd
import os
import numpy as np
import re  # For regex pattern matching
import datetime  # For timestamp in loadouts
import altair as alt

# Set page configuration
st.set_page_config(
    page_title="F1 Clash Data Manager",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# File paths
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

# Utility functions
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

def import_special_csv_formats():
    st.header("Import Specialized CSV Formats")
    st.markdown("""
    This section is designed to import data from the specific CSV format structure used in F1 Clash spreadsheets.
    It supports the following formats:
    - Components Vertical CSV - with component types as section headers
    - Drivers Vertical Combined CSV - with driver stats and details
    - Data Input & Tracker CSV - with level requirements and card tracking
    """)
    
    # Helper function to clean numeric values (remove commas)
    def clean_numeric(value):
        """Remove commas from numeric strings and convert to int or float."""
        if isinstance(value, str):
            return value.replace(',', '')
        return value
        
    # Helper function to safely convert to int
    def safe_int(value):
        """Safely convert a value to int, handling commas and returning 0 if invalid."""
        if pd.isna(value):
            return 0
        try:
            # First remove any commas
            if isinstance(value, str):
                value = value.replace(',', '')
            return int(float(value))
        except (ValueError, TypeError):
            return 0
            
    # Helper function to safely convert to float
    def safe_float(value):
        """Safely convert a value to float, handling commas and returning 0.0 if invalid."""
        if pd.isna(value):
            return 0.0
        try:
            # First remove any commas
            if isinstance(value, str):
                value = value.replace(',', '')
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    # Create tabs for different import types
    tab1, tab2, tab3 = st.tabs(["Components Import", "Drivers Import", "Tracker Data Import"])
    
    with tab1:
        st.subheader("Import Components from Vertical Format")
        st.write("Upload your Components Vertical CSV file with section headers (BRAKES, GEARBOX, etc.)")
        
        uploaded_file = st.file_uploader("Choose Components CSV file", type="csv", key="components_vertical_uploader")
        
        if uploaded_file is not None:
            try:
                # Read the CSV file - skip initial rows as they might contain headers
                raw_df = pd.read_csv(uploaded_file, header=None)
                
                st.write("Preview of raw data:")
                st.dataframe(raw_df.head(20), use_container_width=True)
                
                if st.button("Process and Import Components", key="process_components_btn"):
                    # Process the CSV - identify component type sections
                    component_sections = {}
                    current_section = None
                    section_start = 0
                    
                    # Find section headers (component types)
                    for i, row in raw_df.iterrows():
                        # Check if this is a section header row (component type)
                        if not pd.isna(row[0]) and row[0].strip().upper() in ["BRAKES", "GEARBOX", "REAR WING", "FRONT WING", "SUSPENSION", "ENGINE"]:
                            # If we've been in a section, store the previous section's data
                            if current_section is not None:
                                component_sections[current_section] = raw_df.iloc[section_start+1:i].dropna(how='all')
                            
                            # Start a new section
                            current_section = row[0].strip()
                            section_start = i
                    
                    # Add the last section
                    if current_section is not None:
                        component_sections[current_section] = raw_df.iloc[section_start+1:].dropna(how='all')
                    
                    # Process each section and update the JSON files
                    updates_by_type = {}
                    for component_type, section_df in component_sections.items():
                        # Get the header row
                        headers = section_df.iloc[0].tolist()
                        
                        # Process data rows
                        data_rows = section_df.iloc[1:].reset_index(drop=True)
                        
                        # Create a list to store component data
                        component_data = []
                        
                        # Map CSV column names to JSON field names
                        for i, row in data_rows.iterrows():
                            if pd.isna(row[0]) or str(row[0]).strip() == "":
                                continue  # Skip empty rows
                            
                            component_name = row[1] if not pd.isna(row[1]) else ""
                            if component_name == "":
                                continue  # Skip rows without a component name
                            
                            # Create a dictionary for this component
                            component = {
                                "name": component_name,
                                "level": safe_int(row[2]),
                                "boost_active": bool(row[3]) if not pd.isna(row[3]) else False,
                                "stats": {
                                    "speed": safe_int(row[4]),
                                    "cornering": safe_int(row[5]),
                                    "powerUnit": safe_int(row[6]),
                                    "qualifying": safe_int(row[7]),
                                    "pitTime": safe_float(row[8])
                                },
                                "totalValue": safe_int(row[9]),
                                "series": safe_int(row[10]),
                                "cards": safe_int(row[11]),
                                "total_cards": safe_int(row[12]),
                                "coins": clean_numeric(row[13]) if not pd.isna(row[13]) else "0",
                                "total_coins": clean_numeric(row[14]) if not pd.isna(row[14]) else "0"
                            }
                            
                            component_data.append(component)
                        
                        updates_by_type[component_type] = component_data
                    
                    # Update the JSON files with the processed data
                    total_updates = 0
                    
                    for component_type, components in updates_by_type.items():
                        # Determine the correct JSON file and key
                        json_key = component_type.lower().replace(" ", "_")
                        file_path = COMPONENT_FILES.get(component_type.title())
                        
                        if file_path:
                            # Load the existing JSON data
                            existing_data = load_json_data(file_path)
                            
                            if existing_data:
                                # Create a lookup for existing components
                                existing_lookup = {c["name"]: c for c in existing_data[json_key]}
                                
                                # Update existing components with data from CSV
                                for component in components:
                                    name = component["name"]
                                    if name in existing_lookup:
                                        # Update stats
                                        existing_lookup[name]["stats"]["speed"] = component["stats"]["speed"]
                                        existing_lookup[name]["stats"]["cornering"] = component["stats"]["cornering"]
                                        existing_lookup[name]["stats"]["powerUnit"] = component["stats"]["powerUnit"]
                                        existing_lookup[name]["stats"]["qualifying"] = component["stats"]["qualifying"]
                                        existing_lookup[name]["stats"]["pitTime"] = component["stats"]["pitTime"]
                                        
                                        # Update other fields, preserving fields not in CSV
                                        existing_lookup[name]["level"] = component["level"]
                                        existing_lookup[name]["totalValue"] = component["stats"]["speed"] + component["stats"]["cornering"] + component["stats"]["powerUnit"] + component["stats"]["qualifying"] + component["stats"]["pitTime"]
                                        existing_lookup[name]["series"] = component["series"]
                                        
                                        # Update card counts if provided
                                        if component["cards"] > 0:
                                            existing_lookup[name]["upgradeInfo"]["cardsOwned"] = component["cards"]
                                            
                                            # Calculate cards needed
                                            max_cards = existing_lookup[name]["upgradeInfo"]["maxCards"]
                                            cards_needed = max(0, max_cards - component["cards"])
                                            existing_lookup[name]["upgradeInfo"]["cardsNeeded"] = cards_needed
                                        
                                        # Update inventory status based on level
                                        existing_lookup[name]["inInventory"] = component["level"] > 0
                                        
                                        total_updates += 1
                                
                                # Save the updated data
                                if save_json_data(existing_data, file_path):
                                    st.success(f"Updated {total_updates} components in {file_path}")
                                else:
                                    st.error(f"Failed to save updates to {file_path}")
                    
                    if total_updates > 0:
                        st.success(f"Successfully updated a total of {total_updates} components")
                    else:
                        st.warning("No components were updated. Check that component names match between CSV and JSON files.")
            
            except Exception as e:
                st.error(f"Error processing Components CSV: {str(e)}")
    
    with tab2:
        st.subheader("Import Drivers from Vertical Format")
        st.write("Upload your Drivers Vertical Combined CSV file with driver stats")
        
        uploaded_file = st.file_uploader("Choose Drivers CSV file", type="csv", key="drivers_vertical_uploader")
        
        if uploaded_file is not None:
            try:
                # Read the CSV file - assuming a header row is present
                drivers_df = pd.read_csv(uploaded_file)
                
                st.write("Preview of driver data:")
                st.dataframe(drivers_df.head(), use_container_width=True)
                
                if st.button("Process and Import Drivers", key="process_drivers_btn"):
                    # Load the existing drivers JSON
                    drivers_data = load_json_data(DRIVERS_FILE)
                    
                    if drivers_data:
                        # Create a lookup for existing drivers
                        existing_lookup = {f"{d['name']}_{d['rarity']}": d for d in drivers_data["drivers"]}
                        
                        # Process each row in the CSV
                        updates_made = 0
                        for _, row in drivers_df.iterrows():
                            # Skip rows without a driver name
                            if pd.isna(row["Drivers"]) or str(row["Drivers"]).strip() == "":
                                continue
                            
                            driver_name = row["Drivers"]
                            driver_rarity = row["Rarity"]
                            
                            # Create lookup key
                            lookup_key = f"{driver_name}_{driver_rarity}"
                            
                            if lookup_key in existing_lookup:
                                driver = existing_lookup[lookup_key]
                                
                                # Update driver stats - safely convert all numeric values
                                driver["stats"]["overtaking"] = safe_int(row["Overtaking"])
                                driver["stats"]["defending"] = safe_int(row["Defending"])
                                driver["stats"]["qualifying"] = safe_int(row["Qualifying"])
                                driver["stats"]["raceStart"] = safe_int(row["Race Start"])
                                driver["stats"]["tyreMgmt"] = safe_int(row["Tyre Mgmt"])
                                
                                # Update level and other fields
                                driver["level"] = safe_int(row["Level"])
                                driver["series"] = safe_int(row["Series"])
                                
                                # Update total value
                                driver["totalValue"] = driver["stats"]["overtaking"] + driver["stats"]["defending"] + driver["stats"]["qualifying"] + driver["stats"]["raceStart"] + driver["stats"]["tyreMgmt"]
                                
                                # Update inventory status based on level
                                driver["inInventory"] = driver["level"] > 0
                                
                                # Update legacy points for legendary drivers
                                if driver["rarity"] == "Legendary" and "Legacy Points" in row and not pd.isna(row["Legacy Points"]):
                                    driver["legacyPoints"] = safe_int(row["Legacy Points"])
                                
                                updates_made += 1
                        
                        # Save the updated data
                        if updates_made > 0:
                            if save_json_data(drivers_data, DRIVERS_FILE):
                                st.success(f"Successfully updated {updates_made} drivers")
                            else:
                                st.error("Failed to save driver updates")
                        else:
                            st.warning("No drivers were updated. Check that driver names and rarities match between CSV and JSON files.")
                    else:
                        st.error("Failed to load drivers data")
            
            except Exception as e:
                st.error(f"Error processing Drivers CSV: {str(e)}")
                st.exception(e)  # Show full error details
    
    with tab3:
        st.subheader("Import Data Input & Tracker")
        st.write("Upload your Data Input & Tracker CSV file with level requirements")
        
        uploaded_file = st.file_uploader("Choose Tracker CSV file", type="csv", key="tracker_uploader")
        
        if uploaded_file is not None:
            try:
                # Read the CSV file
                tracker_df = pd.read_csv(uploaded_file, header=None)
                
                st.write("Preview of tracker data:")
                st.dataframe(tracker_df.head(20), use_container_width=True)
                
                if st.button("Process Tracker Data", key="process_tracker_btn"):
                    # UPDATED APPROACH: The CSV has columns numbered 0-10+
                    # Column 0: Driver names or headers
                    # Column 1: Rarity
                    # Column 2: Level
                    # Column 3: Highest Level (Max level)
                    # Column 4: Cards owned (Amount)
                    # Column 5: Cards needed (Needed)
                    # Column 6: Max cards (Max)
                    
                    # Find the row containing headers like "Drivers", "Rarity", etc.
                    header_row = None
                    for i, row in tracker_df.iterrows():
                        if not pd.isna(row[0]) and str(row[0]).strip() == "Drivers":
                            header_row = i
                            break
                    
                    if header_row is not None:
                        # Use the header row to understand the column structure
                        headers = tracker_df.iloc[header_row].tolist()
                        
                        # Extract the actual data (starting from row after headers)
                        data_start = header_row + 1
                        data_rows = tracker_df.iloc[data_start:].reset_index(drop=True)
                        
                        # Process driver data
                        drivers_json = load_json_data(DRIVERS_FILE)
                        driver_updates = 0
                        
                        if drivers_json:
                            # Create a lookup for existing drivers
                            existing_drivers = {f"{d['name']}_{d['rarity']}": d for d in drivers_json["drivers"]}
                            
                            # Process each driver row
                            for _, row in data_rows.iterrows():
                                # Skip empty rows or rows with no driver name
                                if pd.isna(row[0]) or str(row[0]).strip() == "":
                                    continue
                                
                                # Skip header or section marker rows
                                if str(row[0]).strip() in ["Components", "BRAKES", "GEARBOX", "REAR WING", "FRONT WING", "SUSPENSION", "ENGINE"]:
                                    break
                                
                                driver_name = str(row[0]).strip()
                                
                                # Sometimes the rarity might not be in the CSV, try to get it from existing data
                                driver_rarity = str(row[1]).strip() if not pd.isna(row[1]) else None
                                
                                # Try to find the driver in the existing data
                                found_driver = None
                                
                                # First try with name and rarity
                                if driver_rarity:
                                    lookup_key = f"{driver_name}_{driver_rarity}"
                                    if lookup_key in existing_drivers:
                                        found_driver = existing_drivers[lookup_key]
                                
                                # If not found, try just by name
                                if not found_driver:
                                    # Try to find a driver with matching name
                                    for key, d in existing_drivers.items():
                                        if d['name'] == driver_name:
                                            found_driver = d
                                            # Use the rarity from existing data
                                            driver_rarity = d['rarity']
                                            break
                                
                                if found_driver:
                                    # Update driver information using safe conversion
                                    # Update level
                                    if not pd.isna(row[2]):
                                        found_driver["level"] = safe_int(row[2])
                                    
                                    # Update highest level
                                    if not pd.isna(row[3]):
                                        found_driver["highestLevel"] = safe_int(row[3])
                                    
                                    # Update cards owned
                                    if not pd.isna(row[4]):
                                        found_driver["upgradeInfo"]["cardsOwned"] = safe_int(row[4])
                                    
                                    # Update cards needed
                                    if not pd.isna(row[5]):
                                        found_driver["upgradeInfo"]["cardsNeeded"] = safe_int(row[5])
                                    
                                    # Update max cards
                                    if not pd.isna(row[6]):
                                        found_driver["upgradeInfo"]["maxCards"] = safe_int(row[6])
                                    
                                    # Update inventory status based on level
                                    found_driver["inInventory"] = found_driver["level"] > 0
                                    
                                    driver_updates += 1
                            
                            # Save driver updates
                            if driver_updates > 0:
                                if save_json_data(drivers_json, DRIVERS_FILE):
                                    st.success(f"Updated {driver_updates} drivers with card information")
                                else:
                                    st.error("Failed to save driver updates")
                        else:
                            st.error("Failed to load drivers JSON data")
                        
                        # Now look for the Components section to process components
                        component_section = None
                        for i, row in data_rows.iterrows():
                            if not pd.isna(row[0]) and str(row[0]).strip() == "Components":
                                component_section = i
                                break
                        
                        if component_section is not None:
                            # Skip the Components header row
                            component_data_start = component_section + 1
                            component_rows = data_rows.iloc[component_data_start:].reset_index(drop=True)
                            
                            # Process components by type
                            current_type = None
                            type_start = 0
                            component_sections = {}
                            
                            # Find the different component type sections
                            for i, row in component_rows.iterrows():
                                if pd.isna(row[0]):
                                    continue
                                
                                cell_value = str(row[0]).strip()
                                
                                if cell_value in ["Brakes", "Gearbox", "Rear Wing", "Front Wing", "Suspension", "Engine"]:
                                    # If we've been in a section, store the rows for that section
                                    if current_type is not None:
                                        component_sections[current_type] = component_rows.iloc[type_start:i].copy()
                                    
                                    # Start a new section
                                    current_type = cell_value
                                    type_start = i + 1  # Start after the header row
                            
                            # Add the last section
                            if current_type is not None:
                                component_sections[current_type] = component_rows.iloc[type_start:].copy()
                            
                            # Process each component type
                            component_updates = 0
                            
                            for component_type, comp_df in component_sections.items():
                                # Get the correct JSON file and key
                                file_path = COMPONENT_FILES.get(component_type)
                                json_key = component_type.lower().replace(" ", "_")
                                
                                if file_path:
                                    # Load the existing JSON data
                                    component_json = load_json_data(file_path)
                                    
                                    if component_json:
                                        # Create a lookup for existing components
                                        existing_components = {c["name"]: c for c in component_json[json_key]}
                                        
                                        # Process component data rows
                                        for _, row in comp_df.iterrows():
                                            if pd.isna(row[0]) or str(row[0]).strip() == "":
                                                continue
                                            
                                            component_name = str(row[0]).strip()
                                            
                                            if component_name in existing_components:
                                                component = existing_components[component_name]
                                                
                                                # Update component data using safe conversion
                                                if not pd.isna(row[2]):
                                                    component["level"] = safe_int(row[2])
                                                if not pd.isna(row[3]):
                                                    component["highestLevel"] = safe_int(row[3])
                                                
                                                # Update cards owned
                                                if not pd.isna(row[4]):
                                                    component["upgradeInfo"]["cardsOwned"] = safe_int(row[4])
                                                
                                                # Update cards needed
                                                if not pd.isna(row[5]):
                                                    component["upgradeInfo"]["cardsNeeded"] = safe_int(row[5])
                                                
                                                # Update max cards
                                                if not pd.isna(row[6]):
                                                    component["upgradeInfo"]["maxCards"] = safe_int(row[6])
                                                
                                                # Update inventory status based on level
                                                component["inInventory"] = component["level"] > 0
                                                
                                                component_updates += 1
                                        
                                        # Save component updates
                                        if component_updates > 0:
                                            if save_json_data(component_json, file_path):
                                                st.success(f"Updated components in {file_path}")
                                            else:
                                                st.error(f"Failed to save updates to {file_path}")
                                    else:
                                        st.error(f"Failed to load component JSON data for {component_type}")
                            
                            if component_updates > 0:
                                st.success(f"Updated a total of {component_updates} components with card information")
                        else:
                            st.warning("Could not find the Components section in the tracker file")
                    else:
                        st.error("Could not find the Drivers section in the tracker file. Make sure your CSV has a row with 'Drivers' in the first column.")
            
            except Exception as e:
                st.error(f"Error processing Tracker CSV: {str(e)}")
                st.exception(e)  # This will show the full stack trace

# Driver management
def manage_drivers():
    global data
    
    st.header("Driver Management")
    
    # Load driver data
    data = load_json_data(DRIVERS_FILE)
    if not data:
        st.error("Failed to load driver data")
        return
    
    # Add CSV import/export functionality
    st.subheader("Import/Export CSV")
    
    # Create columns for the import/export functionality
    csv_col1, csv_col2 = st.columns(2)
    
    with csv_col1:
        st.write("Export drivers data to CSV for editing in Excel/spreadsheet:")
        if st.button("Export Drivers to CSV"):
            # Create a dataframe with all relevant driver data
            export_df = pd.DataFrame([{
                "Name": d["name"],
                "Rarity": d["rarity"],
                "Level": d["level"],
                "Max Level": d["highestLevel"],
                "Cards": d["upgradeInfo"]["cardsOwned"],
                "Cards Needed": d["upgradeInfo"]["cardsNeeded"],
                "Max Cards": d["upgradeInfo"]["maxCards"],
                "Coins Needed": d["upgradeInfo"]["coinsNeeded"],
                "Total Value": d["totalValue"],
                "Series": d["series"],
                "In Inventory": d["inInventory"],
                "Overtaking": d["stats"]["overtaking"],
                "Defending": d["stats"]["defending"],
                "Qualifying": d["stats"]["qualifying"],
                "Race Start": d["stats"]["raceStart"],
                "Tyre Mgmt": d["stats"]["tyreMgmt"]
            } for d in data["drivers"]])
            
            # Convert to CSV
            csv = export_df.to_csv(index=False)
            
            # Create a download button
            st.download_button(
                label="Download CSV File",
                data=csv,
                file_name="drivers_data.csv",
                mime="text/csv"
            )
            st.success("CSV file ready for download")
    
    with csv_col2:
        st.write("Import drivers data from CSV after editing:")
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv", key="driver_csv_uploader")
        
        if uploaded_file is not None:
            # Read the CSV file
            try:
                import_df = pd.read_csv(uploaded_file)
                st.write("Preview of CSV data:")
                st.dataframe(import_df.head(), use_container_width=True)
                
                if st.button("Import and Update Drivers"):
                    # Create a dictionary to look up drivers by name and rarity
                    driver_lookup = {f"{d['name']}_{d['rarity']}": d for d in data["drivers"]}
                    updates_made = 0
                    
                    # Update the JSON data with values from the CSV
                    for _, row in import_df.iterrows():
                        lookup_key = f"{row['Name']}_{row['Rarity']}"
                        
                        if lookup_key in driver_lookup:
                            driver = driver_lookup[lookup_key]
                            driver_idx = data["drivers"].index(driver)
                            
                            # Update all fields from the CSV using safe conversion functions
                            data["drivers"][driver_idx]["level"] = safe_int(row["Level"])
                            data["drivers"][driver_idx]["highestLevel"] = safe_int(row["Max Level"])
                            data["drivers"][driver_idx]["upgradeInfo"]["cardsOwned"] = safe_int(row["Cards"])
                            data["drivers"][driver_idx]["upgradeInfo"]["cardsNeeded"] = safe_int(row["Cards Needed"])
                            data["drivers"][driver_idx]["upgradeInfo"]["coinsNeeded"] = safe_int(row["Coins Needed"])
                            data["drivers"][driver_idx]["totalValue"] = safe_int(row["Total Value"])
                            data["drivers"][driver_idx]["series"] = safe_int(row["Series"])
                            data["drivers"][driver_idx]["inInventory"] = bool(row["In Inventory"])
                            
                            # Update stats
                            data["drivers"][driver_idx]["stats"]["overtaking"] = safe_int(row["Overtaking"])
                            data["drivers"][driver_idx]["stats"]["defending"] = safe_int(row["Defending"])
                            data["drivers"][driver_idx]["stats"]["qualifying"] = safe_int(row["Qualifying"])
                            data["drivers"][driver_idx]["stats"]["raceStart"] = safe_int(row["Race Start"])
                            data["drivers"][driver_idx]["stats"]["tyreMgmt"] = safe_int(row["Tyre Mgmt"])
                            
                            updates_made += 1
                    
                    # Save the updated data
                    if updates_made > 0:
                        if save_json_data(data, DRIVERS_FILE):
                            st.success(f"Successfully updated {updates_made} drivers from CSV")
                        else:
                            st.error("Failed to save changes from CSV import")
                    else:
                        st.warning("No matching drivers found in the CSV file")
            except Exception as e:
                st.error(f"Error processing CSV file: {e}")
                st.exception(e)  # Show full stack trace
    
    st.markdown("---")
    
    # Create a dataframe for display - remove 'Cards Needed' from visualization
    drivers_df = pd.DataFrame([{
        "Name": d["name"],
        "Rarity": d["rarity"],
        "Level": d["level"],
        "Max Level": d["highestLevel"],
        "Cards": d["upgradeInfo"]["cardsOwned"],
        "Total Value": d["totalValue"],
        "Series": d["series"],
        "In Inventory": d["inInventory"],
        "Overtaking": d["stats"]["overtaking"],
        "Defending": d["stats"]["defending"],
        "Qualifying": d["stats"]["qualifying"],
        "Race Start": d["stats"]["raceStart"],
        "Tyre Mgmt": d["stats"]["tyreMgmt"]
    } for d in data["drivers"]])
    
    # Add filters in sidebar
    st.sidebar.subheader("Driver Filters")
    rarities = ["All"] + sorted(drivers_df["Rarity"].unique().tolist())
    selected_rarity = st.sidebar.selectbox("Filter by Rarity", rarities, key="driver_rarity")
    
    series = ["All"] + sorted(drivers_df["Series"].unique().tolist())
    selected_series = st.sidebar.selectbox("Filter by Series", series, key="driver_series")
    
    show_inventory_only = st.sidebar.checkbox("Show only drivers in inventory", key="driver_inventory")
    
    # Apply filters
    filtered_df = drivers_df.copy()
    if selected_rarity != "All":
        filtered_df = filtered_df[filtered_df["Rarity"] == selected_rarity]
    if selected_series != "All":
        filtered_df = filtered_df[filtered_df["Series"] == selected_series]
    if show_inventory_only:
        filtered_df = filtered_df[filtered_df["In Inventory"] == True]
    
    # Display filtered drivers with read-only table
    st.subheader(f"Drivers ({len(filtered_df)} of {len(drivers_df)})")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    
    st.info("To edit driver information, please use the CSV export/import functionality above.")

# Component management
def manage_components(component_type):
    """Function to manage components of a specific type"""
    global component_files
    
    lower_type = component_type.lower().replace(" ", "_")
    file_path = COMPONENT_FILES.get(component_type)
    
    if not file_path:
        st.error(f"No file path defined for component type: {component_type}")
        return
    
    st.header(f"{component_type} Management")
    
    # Load component data
    component_json = load_json_data(file_path)
    if not component_json:
        st.error(f"Failed to load {component_type} data")
        return
    
    components = component_json.get(lower_type, [])
    
    # Add CSV import/export functionality
    st.subheader("Import/Export CSV")
    
    # Create columns for the import/export functionality
    csv_col1, csv_col2 = st.columns(2)
    
    with csv_col1:
        st.write(f"Export {component_type} data to CSV for editing in Excel/spreadsheet:")
        if st.button(f"Export {component_type} to CSV"):
            # Create a dataframe with all relevant component data
            export_df = pd.DataFrame([{
                "Name": comp["name"],
                "Rarity": comp["rarity"],
                "Level": comp["level"],
                "Max Level": comp["highestLevel"],
                "Speed": comp["stats"]["speed"],
                "Cornering": comp["stats"]["cornering"],
                "Power Unit": comp["stats"]["powerUnit"],
                "Qualifying": comp["stats"]["qualifying"],
                "Pit Time": comp["stats"]["pitTime"],
                "Total Value": comp["totalValue"],
                "Series": comp["series"],
                "In Inventory": comp["inInventory"],
                "Cards Owned": comp["upgradeInfo"]["cardsOwned"],
                "Cards Needed": comp["upgradeInfo"]["cardsNeeded"],
                "Max Cards": comp["upgradeInfo"]["maxCards"],
                "Coins Needed": comp["upgradeInfo"]["coinsNeeded"]
            } for comp in components])
            
            # Convert to CSV
            csv = export_df.to_csv(index=False)
            
            # Create a download button
            st.download_button(
                label="Download CSV File",
                data=csv,
                file_name=f"{component_type.lower()}_data.csv",
                mime="text/csv"
            )
            st.success("CSV file ready for download")
    
    with csv_col2:
        st.write(f"Import {component_type} data from CSV after editing:")
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv", key=f"{component_type}_csv_uploader")
        
        if uploaded_file is not None:
            # Read the CSV file
            try:
                import_df = pd.read_csv(uploaded_file)
                st.write("Preview of CSV data:")
                st.dataframe(import_df.head(), use_container_width=True)
                
                if st.button(f"Import and Update {component_type}"):
                    # Create a dictionary to look up components by name
                    component_lookup = {comp["name"]: comp for comp in components}
                    updates_made = 0
                    
                    # Update the JSON data with values from the CSV
                    for _, row in import_df.iterrows():
                        component_name = row["Name"]
                        
                        if component_name in component_lookup:
                            comp = component_lookup[component_name]
                            comp_idx = components.index(comp)
                            
                            # Update basic fields using safe conversion
                            components[comp_idx]["level"] = safe_int(row["Level"])
                            components[comp_idx]["highestLevel"] = safe_int(row["Max Level"])
                            components[comp_idx]["inInventory"] = bool(row["In Inventory"])
                            components[comp_idx]["series"] = safe_int(row["Series"])
                            components[comp_idx]["rarity"] = row["Rarity"]
                            
                            # Update stats - ensure all are float
                            components[comp_idx]["stats"]["speed"] = safe_float(row["Speed"])
                            components[comp_idx]["stats"]["cornering"] = safe_float(row["Cornering"])
                            components[comp_idx]["stats"]["powerUnit"] = safe_float(row["Power Unit"])
                            components[comp_idx]["stats"]["qualifying"] = safe_float(row["Qualifying"])
                            components[comp_idx]["stats"]["pitTime"] = safe_float(row["Pit Time"])
                            
                            # Update total value
                            components[comp_idx]["totalValue"] = safe_float(row["Total Value"])
                            
                            # Update upgrade info
                            components[comp_idx]["upgradeInfo"]["cardsOwned"] = safe_int(row["Cards Owned"])
                            components[comp_idx]["upgradeInfo"]["cardsNeeded"] = safe_int(row["Cards Needed"])
                            components[comp_idx]["upgradeInfo"]["coinsNeeded"] = safe_float(row["Coins Needed"])
                            
                            updates_made += 1
                    
                    # Save the updated data
                    if updates_made > 0:
                        if save_json_data(component_json, file_path):
                            st.success(f"Successfully updated {updates_made} {component_type} components from CSV")
                        else:
                            st.error("Failed to save changes from CSV import")
                    else:
                        st.warning(f"No matching {component_type} components found in the CSV file")
            except Exception as e:
                st.error(f"Error processing CSV file: {e}")
                st.exception(e)  # Show the full stack trace
    
    st.markdown("---")
    
    # Display components in a table
    st.subheader(f"Available {component_type}")
    
    if components:
        # Create a DataFrame from components for display - removed Cards Needed
        comp_data = []
        for comp in components:
            comp_data.append({
                "Name": comp["name"],
                "Rarity": comp["rarity"],
                "Level": comp["level"],
                "Max Level": comp["highestLevel"],
                "Speed": comp["stats"]["speed"],
                "Cornering": comp["stats"]["cornering"],
                "Power Unit": comp["stats"]["powerUnit"],
                "Qualifying": comp["stats"]["qualifying"],
                "Pit Time": comp["stats"]["pitTime"],
                "Total Value": comp["totalValue"],
                "Series": comp["series"],
                "In Inventory": comp["inInventory"]
            })
        
        # Add filters in sidebar
        st.sidebar.subheader(f"{component_type} Filters")
        
        # Rarity filter
        rarities = ["All"] + sorted(set(comp["Rarity"] for comp in comp_data))
        selected_rarity = st.sidebar.selectbox(f"Filter by Rarity", rarities, key=f"{component_type}_rarity")
        
        # Inventory filter
        show_inventory_only = st.sidebar.checkbox(f"Show only {component_type} in inventory", key=f"{component_type}_inventory")
        
        # Apply filters
        filtered_comp_data = comp_data.copy()
        if selected_rarity != "All":
            filtered_comp_data = [comp for comp in filtered_comp_data if comp["Rarity"] == selected_rarity]
        if show_inventory_only:
            filtered_comp_data = [comp for comp in filtered_comp_data if comp["In Inventory"]]
        
        # Display the filtered components
        if filtered_comp_data:
            df = pd.DataFrame(filtered_comp_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info(f"No {component_type} match the selected filters")
    else:
        st.info(f"No {component_type} data available")
    
    st.info("To edit component information, please use the CSV export/import functionality above.")

# Track management
def manage_tracks():
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
    
    # Create track dataframe
    tracks_df = pd.DataFrame([{
        "Name": t["name"],
        "Primary Attribute": t["primary_attribute"],
        "Focus": t["focus"],
        "Recommended Boosts": len(t.get("boosts", []))
    } for t in tracks])
    
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
    st.dataframe(filtered_df, use_container_width=True)
    
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
            track_groups = []
            for boost in boosts:
                if "track_groups" in boost:
                    for group in boost["track_groups"]:
                        if selected_track_name in group:
                            if group not in track_groups:
                                track_groups.append(group)
            
            if track_groups:
                st.markdown(f"**Track Groups:** {', '.join(track_groups)}")
        
        # Display recommended boosts
        st.subheader("Recommended Boosts")
        
        track_boosts = selected_track.get("boosts", [])
        
        if track_boosts:
            boost_df = pd.DataFrame([{
                "Boost": b["name"],
                "Primary Stat": selected_track['primary_attribute'],
                "Primary Value": b.get("stats", {}).get(selected_track['primary_attribute'].lower().replace(" ", "_"), 0),
                "Focus Stat": selected_track['focus'],
                "Focus Value": b.get("stats", {}).get(selected_track['focus'].lower().replace(" ", "_"), 0),
                "Final Stat": b.get("final_stat", ""),
                "Final Value": b.get("final_value", 0)
            } for b in track_boosts])
            
            st.dataframe(boost_df, use_container_width=True, hide_index=True)
        else:
            st.info("No recommended boosts for this track")

# Series setup management
def manage_series_setups():
    st.header("Series Setup Management")
    
    # Load series setup data
    data = load_json_data(SERIES_SETUPS_FILE)
    
    if not data:
        st.error("Failed to load series setup data")
        return
    
    series_setups = data.get("series_setups", [])
    
    # Create sidebar selection for series
    st.sidebar.subheader("Series Selection")
    series_numbers = [s["series"] for s in series_setups]
    selected_series = st.sidebar.selectbox("Select Series", series_numbers)
    
    # Find selected series
    selected_setup = next((s for s in series_setups if s["series"] == selected_series), None)
    
    if not selected_setup:
        st.warning(f"No setup data found for Series {selected_series}")
        return
    
    # Display series setup
    st.subheader(f"Series {selected_series} Setups")
    
    # Create tabs for different focus areas
    tab1, tab2, tab3 = st.tabs(["Speed", "Cornering", "Power Unit"])
    
    # Helper function to display setup
    def display_setup(setup, focus):
        df = pd.DataFrame([{
            "Component": s["component"],
            "Value": float(s["value"])  # Ensure values are treated as floats
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
    
    # Display each focus area
    with tab1:
        display_setup(selected_setup["setups"]["speed"], "Speed")
    
    with tab2:
        display_setup(selected_setup["setups"]["cornering"], "Cornering")
    
    with tab3:
        display_setup(selected_setup["setups"]["power_unit"], "Power Unit")

def manage_loadouts():
    """
    Function to manage saved car and driver loadouts
    """
    st.header("F1 Clash Loadouts Manager")
    st.write("Create, edit, and manage your saved car and driver loadouts")
    
    # Load loadouts data
    loadouts_data = load_json_data(LOADOUTS_FILE)
    if not loadouts_data:
        st.error("Failed to load loadouts data.")
        return
    
    loadouts = loadouts_data.get("loadouts", [])
    
    # Create tabs for viewing and editing loadouts
    tab1, tab2 = st.tabs(["View Loadouts", "Compare Loadouts"])
    
    with tab1:
        st.subheader("Saved Loadouts")
        
        # Create a dropdown to select a loadout
        loadout_titles = [f"{l['id']}. {l['title']}" for l in loadouts]
        
        if not loadout_titles:
            st.info("No loadouts available. Create one in the 'Edit Loadout' tab.")
            return
            
        selected_loadout_index = st.selectbox("Select a loadout to view", range(len(loadout_titles)), 
                                             format_func=lambda x: loadout_titles[x])
        
        loadout = loadouts[selected_loadout_index]
        
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
                f"{car_stats['speed']:.1f}".rstrip('0').rstrip('.') if '.' in f"{car_stats['speed']:.1f}" else f"{car_stats['speed']:.1f}",
                f"{car_stats['cornering']:.1f}".rstrip('0').rstrip('.') if '.' in f"{car_stats['cornering']:.1f}" else f"{car_stats['cornering']:.1f}",
                f"{car_stats['power_unit']:.1f}".rstrip('0').rstrip('.') if '.' in f"{car_stats['power_unit']:.1f}" else f"{car_stats['power_unit']:.1f}",
                f"{car_stats['qualifying']:.1f}".rstrip('0').rstrip('.') if '.' in f"{car_stats['qualifying']:.1f}" else f"{car_stats['qualifying']:.1f}",
                f"{car_stats['pit_time']:.2f}",
                f"{car_stats['total_car_value']:.1f}".rstrip('0').rstrip('.') if '.' in f"{car_stats['total_car_value']:.1f}" else f"{car_stats['total_car_value']:.1f}"
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
            components_data["Speed"].append(f"{component['stats']['speed']:.1f}".rstrip('0').rstrip('.') if '.' in f"{component['stats']['speed']:.1f}" else f"{component['stats']['speed']:.1f}")
            components_data["Cornering"].append(f"{component['stats']['cornering']:.1f}".rstrip('0').rstrip('.') if '.' in f"{component['stats']['cornering']:.1f}" else f"{component['stats']['cornering']:.1f}")
            components_data["Power Unit"].append(f"{component['stats']['power_unit']:.1f}".rstrip('0').rstrip('.') if '.' in f"{component['stats']['power_unit']:.1f}" else f"{component['stats']['power_unit']:.1f}")
            components_data["Qualifying"].append(f"{component['stats']['qualifying']:.1f}".rstrip('0').rstrip('.') if '.' in f"{component['stats']['qualifying']:.1f}" else f"{component['stats']['qualifying']:.1f}")
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
            driver_stats_data[driver_col] = [
                driver['stats']['overtaking'],
                driver['stats']['defending'],
                driver['stats']['qualifying'],
                driver['stats'].get('race_start', driver['stats'].get('raceStart', 0)),
                driver['stats'].get('tyre_mgmt', driver['stats'].get('tyreMgmt', 0)),
                sum([
                    driver['stats']['overtaking'],
                    driver['stats']['defending'],
                    driver['stats']['qualifying'],
                    driver['stats'].get('race_start', driver['stats'].get('raceStart', 0)),
                    driver['stats'].get('tyre_mgmt', driver['stats'].get('tyreMgmt', 0))
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
                
        # Add combined stats column - handle both key formats
        driver_stats_data["Combined"] = [
            driver_stats['overtaking'],
            driver_stats['defending'],
            driver_stats['qualifying'],
            driver_stats.get('raceStart', driver_stats.get('race_start', 0)),
            driver_stats.get('tyreMgmt', driver_stats.get('tyre_mgmt', 0)),
            driver_stats['total_driver_value']
        ]
        
        driver_stats_df = pd.DataFrame(driver_stats_data)
        st.dataframe(driver_stats_df, use_container_width=True, hide_index=True)
        
        st.info(f"Total Loadout Value: {f'{loadout['calculations']['total_value']:.1f}'.rstrip('0').rstrip('.') if '.' in f'{loadout['calculations']['total_value']:.1f}' else f'{loadout['calculations']['total_value']:.1f}'}")
    
    with tab2:
        st.subheader("Loadouts Comparison")
        st.write("Compare all your loadout setups side by side")
        
        # Create comparison dataframe
        comparison_data = []
        
        for loadout in loadouts:
            # Get car stats
            car_stats = loadout['calculations']['car_stats']
            
            # Format numbers to remove trailing zeros
            speed_str = f"{car_stats['speed']:.1f}".rstrip('0').rstrip('.') if '.' in f"{car_stats['speed']:.1f}" else f"{car_stats['speed']:.1f}"
            cornering_str = f"{car_stats['cornering']:.1f}".rstrip('0').rstrip('.') if '.' in f"{car_stats['cornering']:.1f}" else f"{car_stats['cornering']:.1f}"
            power_unit_str = f"{car_stats['power_unit']:.1f}".rstrip('0').rstrip('.') if '.' in f"{car_stats['power_unit']:.1f}" else f"{car_stats['power_unit']:.1f}"
            qualifying_str = f"{car_stats['qualifying']:.1f}".rstrip('0').rstrip('.') if '.' in f"{car_stats['qualifying']:.1f}" else f"{car_stats['qualifying']:.1f}"
            pit_time_str = f"{car_stats['pit_time']:.2f}"
            total_value_str = f"{loadout['calculations']['total_value']:.1f}".rstrip('0').rstrip('.') if '.' in f"{loadout['calculations']['total_value']:.1f}" else f"{loadout['calculations']['total_value']:.1f}"
            
            # Create a row for each loadout
            comparison_data.append({
                "ID": loadout['id'],
                "Title": loadout['title'],
                "Speed": car_stats['speed'],
                "Cornering": car_stats['cornering'],
                "Power Unit": car_stats['power_unit'],
                "Qualifying": car_stats['qualifying'],
                "Pit Time": car_stats['pit_time'],
                "Total Value": loadout['calculations']['total_value'],
                # For display
                "Speed_display": speed_str,
                "Cornering_display": cornering_str,
                "Power Unit_display": power_unit_str,
                "Qualifying_display": qualifying_str,
                "Pit Time_display": pit_time_str,
                "Total Value_display": total_value_str
            })
        
        # Create and display dataframe
        if comparison_data:
            comparison_df = pd.DataFrame(comparison_data)
            
            # Create a display dataframe with numeric values for proper sorting
            # but formatted text for display
            display_df = pd.DataFrame({
                "ID": comparison_df["ID"],
                "Title": comparison_df["Title"],
                "Speed": comparison_df["Speed"],
                "Cornering": comparison_df["Cornering"],
                "Power Unit": comparison_df["Power Unit"],
                "Qualifying": comparison_df["Qualifying"],
                "Pit Time": comparison_df["Pit Time"],
                "Total Value": comparison_df["Total Value"]
            })
            
            # Find max values for highlighting
            max_speed = comparison_df["Speed"].max()
            max_cornering = comparison_df["Cornering"].max()
            max_power_unit = comparison_df["Power Unit"].max()
            max_qualifying = comparison_df["Qualifying"].max()
            max_total = comparison_df["Total Value"].max()
            min_pit = comparison_df["Pit Time"].min()
            
            # Use a darker green for better contrast with white text
            highlight_color = 'forestgreen'
            
            # Use string formatting for display
            for idx, row in comparison_df.iterrows():
                display_df.at[idx, "Speed"] = row["Speed_display"]
                display_df.at[idx, "Cornering"] = row["Cornering_display"]
                display_df.at[idx, "Power Unit"] = row["Power Unit_display"]
                display_df.at[idx, "Qualifying"] = row["Qualifying_display"]
                display_df.at[idx, "Pit Time"] = row["Pit Time_display"]
                display_df.at[idx, "Total Value"] = row["Total Value_display"]
            
            # Create highlight styling functions using the pre-computed maximums
            def highlight_max(s, props=''):
                return np.where(s == s.max(), f"background-color: {highlight_color}; color: white", props)
            
            def highlight_min(s, props=''):
                return np.where(s == s.min(), f"background-color: {highlight_color}; color: white", props)
            
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
            
            # Create bar chart comparing Speed, Cornering, Power Unit, and Qualifying
            chart_data = comparison_df[['Title', 'Speed', 'Cornering', 'Power Unit', 'Qualifying']]
            chart_data = chart_data.melt('Title', var_name='Stat', value_name='Value')
            
            chart = alt.Chart(chart_data).mark_bar().encode(
                x='Title:N',
                y='Value:Q',
                color='Stat:N',
                tooltip=['Title', 'Stat', 'Value']
            ).properties(
                height=400
            ).interactive()
            
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No loadouts available for comparison.")

# Main function
def main():
    st.title("F1 Clash Data Manager")
    
    # Navigation sidebar
    st.sidebar.title("Navigation")
    section = st.sidebar.radio(
        "Select Section",
        ["Drivers", "Components", "Tracks & Boosts", "Series Setups", "Loadouts", "CSV Imports"],
        index=0
    )
    
    # Display the appropriate section
    if section == "Drivers":
        manage_drivers()
    elif section == "Tracks & Boosts":
        manage_tracks()
    elif section == "Series Setups":
        manage_series_setups()
    elif section == "CSV Imports":
        import_special_csv_formats()
    elif section == "Loadouts":
        manage_loadouts()
    elif section == "Components":
        # Create sub-navigation for components
        component_type = st.sidebar.radio(
            "Select Component Type",
            ["Brakes", "Gearbox", "Rear Wing", "Front Wing", "Suspension", "Engine"],
            index=0
        )
        manage_components(component_type)
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.info("F1 Clash Data Manager v1.4")

if __name__ == "__main__":
    main() 