import streamlit as st
import pandas as pd
import json
import os
from .data_manager import load_json_data, save_json_data, DRIVERS_FILE, COMPONENT_FILES, TRACK_BOOSTS_FILE, SERIES_SETUPS_FILE, BOOSTS_FILE
from .utils import safe_int, safe_float

# Add the path to the series data file
SERIES_DATA_FILE = "series_data.json"

def import_special_csv_formats():
    """
    Function to import data from special CSV formats.
    This allows importing data from external tools like Excel and Google Sheets.
    """
    st.header("Import Tools")
    st.write("Import data from CSV files to update your game information")
    
    # Create tabs for different import types
    tab1, tab2, tab3, tab4 = st.tabs([
        "Components Import", 
        "Drivers Import", 
        "Tracker Data Import",
        "Series Info CSV"
    ])
    
    with tab1:
        st.subheader("Import Components")
        st.write("Upload your component CSV file")
        
        # Clean numeric fields option
        clean_numeric = st.checkbox("Clean numeric fields (removes non-numeric characters)", value=True)
        
        # File upload
        uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"], key="components_csv")
        
        if uploaded_file is not None:
            try:
                # Read the CSV file
                df = pd.read_csv(uploaded_file)
                
                # Display the dataframe
                st.write("Preview of the imported data:")
                st.dataframe(df.head())
                
                # Determine the format
                if "Component Name" in df.columns and "Component Type" in df.columns:
                    st.write("Detected format: Components (vertical format)")
                    
                    # Process and save the data
                    if st.button("Process and Save Components"):
                        if import_components_vertical(clean_numeric)(df):
                            st.success("Successfully imported component data!")
                        else:
                            st.error("Failed to import component data.")
                else:
                    st.error("Could not determine the CSV format. Please check your file.")
                    
            except Exception as e:
                st.error(f"Error processing the file: {str(e)}")
    
    with tab2:
        st.subheader("Import Drivers")
        st.write("Upload your drivers CSV file")
        
        # Clean numeric fields option
        clean_numeric_drivers = st.checkbox("Clean numeric fields (removes non-numeric characters)", value=True, key="clean_numeric_drivers")
        
        # File upload
        uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"], key="drivers_csv")
        
        if uploaded_file is not None:
            try:
                # Read the CSV file
                df = pd.read_csv(uploaded_file)
                
                # Display the dataframe
                st.write("Preview of the imported data:")
                st.dataframe(df.head())
                
                # Determine the format
                if "Driver" in df.columns:
                    st.write("Detected format: Drivers")
                    
                    # Process and save the data
                    if st.button("Process and Save Drivers"):
                        if import_drivers(clean_numeric_drivers)(df):
                            st.success("Successfully imported driver data!")
                        else:
                            st.error("Failed to import driver data.")
                else:
                    st.error("Could not determine the CSV format. Please check your file.")
                    
            except Exception as e:
                st.error(f"Error processing the file: {str(e)}")
    
    with tab3:
        st.subheader("Import Tracker Data")
        st.write("Upload your F1 Clash Tracker CSV export")
        
        # Clean numeric fields option
        clean_numeric_tracker = st.checkbox("Clean numeric fields (removes non-numeric characters)", value=True, key="clean_numeric_tracker")
        
        # File upload
        uploaded_file = st.file_uploader("Choose Tracker CSV file", type=["csv"], key="tracker_csv")
        
        if uploaded_file is not None:
            try:
                # Read the CSV file
                df = pd.read_csv(uploaded_file)
                
                # Display the dataframe
                st.write("Preview of the tracker data:")
                st.dataframe(df.head())
                
                # Process and save the data
                if st.button("Process and Save Tracker Data"):
                    if import_tracker_data(clean_numeric_tracker)(df):
                        st.success("Successfully imported tracker data!")
                    else:
                        st.error("Failed to import tracker data.")
                        
            except Exception as e:
                st.error(f"Error processing Tracker CSV: {str(e)}")
                st.exception(e)  # This will show the full stack trace 
    
    with tab4:
        st.subheader("Import Series Information")
        st.write("Import series information from the F1 Clash 2024 Resource Sheet CSV")
        
        # File upload
        uploaded_file = st.file_uploader("Upload Series Information CSV", type=["csv"], key="series_info_csv")
        
        if uploaded_file is not None:
            try:
                # Read the CSV file
                df = pd.read_csv(uploaded_file)
                
                # Display the dataframe
                st.write("Preview of the series data:")
                st.dataframe(df.head())
                
                # Process and save the data
                if st.button("Process and Save Series Data"):
                    if import_series_info_from_df(df):
                        st.success("Successfully imported series information!")
                    else:
                        st.error("Failed to import series information.")
                        
            except Exception as e:
                st.error(f"Error processing the file: {str(e)}")
                st.exception(e)

def import_components_vertical(clean_numeric):
    """Import components from a vertical format CSV"""
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
            st.exception(e)

def import_drivers_vertical():
    """Import drivers from a vertical format CSV"""
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

def import_tracker_data(clean_numeric):
    """Import data from a tracker CSV format"""
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

def import_series_setups_from_df(df):
    """Import series setups from DataFrame"""
    try:
        # Check if the DataFrame has the expected columns
        required_columns = ["Series", "Track Stats", "Recommend TS"]
        for col in required_columns:
            if col not in df.columns:
                st.error(f"Required column '{col}' not found in the CSV file.")
                return False
        
        # Process the data
        series_data = []
        for _, row in df.iterrows():
            series_num = safe_int(row["Series"])
            if series_num is None:
                continue
                
            series_info = {
                "series": series_num,
                "track_stats": row["Track Stats"] if pd.notna(row["Track Stats"]) else "Unknown",
                "recommended_ts": row["Recommend TS"] if pd.notna(row["Recommend TS"]) else "0",
                "coins": safe_int(row["Coins"]) if "Coins" in row and pd.notna(row["Coins"]) else 0,
                "flags_to_unlock": safe_int(row["Flags to unlock"]) if "Flags to unlock" in row and pd.notna(row["Flags to unlock"]) else 0,
                "max_flags": safe_int(row["Max Flags"]) if "Max Flags" in row and pd.notna(row["Max Flags"]) else 0,
                "bot_ts": row["Bot TS"] if "Bot TS" in row and pd.notna(row["Bot TS"]) else "0"
            }
            
            series_data.append(series_info)
        
        # Add Grand Prix as a special series if not already present
        if not any(s["series"] == 0 for s in series_data):
            series_data.append({
                "series": 0,
                "track_stats": "Custom",
                "recommended_ts": "1000+",
                "coins": 0,
                "flags_to_unlock": 0,
                "max_flags": 0,
                "bot_ts": "Varies"
            })
        
        # Sort by series number
        series_data.sort(key=lambda x: x["series"])
        
        # Save to JSON file
        with open(SERIES_SETUPS_FILE, 'w') as f:
            json.dump({"series_data": series_data}, f, indent=2)
        
        return True
    except Exception as e:
        st.error(f"Error importing series setups: {str(e)}")
        st.exception(e)
        return False

def import_series_info_from_df(df):
    """Import series information from DataFrame"""
    try:
        # Check if the DataFrame has the expected columns
        required_columns = ["Series", "Track Stats", "Recommend TS"]
        for col in required_columns:
            if col not in df.columns:
                st.error(f"Required column '{col}' not found in the CSV file.")
                return False
        
        # Process the data
        series_data = []
        for _, row in df.iterrows():
            series_num = safe_int(row["Series"])
            if series_num is None:
                continue
                
            series_info = {
                "series": series_num,
                "track_stats": row["Track Stats"] if pd.notna(row["Track Stats"]) else "Unknown",
                "recommended_ts": row["Recommend TS"] if pd.notna(row["Recommend TS"]) else "0",
                "coins": safe_int(row["Coins"]) if "Coins" in row and pd.notna(row["Coins"]) else 0,
                "flags_to_unlock": safe_int(row["Flags to unlock"]) if "Flags to unlock" in row and pd.notna(row["Flags to unlock"]) else 0,
                "max_flags": safe_int(row["Max Flags"]) if "Max Flags" in row and pd.notna(row["Max Flags"]) else 0,
                "bot_ts": row["Bot TS"] if "Bot TS" in row and pd.notna(row["Bot TS"]) else "0"
            }
            
            series_data.append(series_info)
        
        # Add Grand Prix as a special series if not already present
        if not any(s["series"] == 0 for s in series_data):
            series_data.append({
                "series": 0,
                "track_stats": "Custom",
                "recommended_ts": "1000+",
                "coins": 0,
                "flags_to_unlock": 0,
                "max_flags": 0,
                "bot_ts": "Varies"
            })
        
        # Sort by series number
        series_data.sort(key=lambda x: x["series"])
        
        # Save to JSON file
        with open(SERIES_DATA_FILE, 'w') as f:
            json.dump({"series_data": series_data}, f, indent=2)
        
        return True
    except Exception as e:
        st.error(f"Error importing series information: {str(e)}")
        st.exception(e)
        return False 