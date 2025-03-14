import streamlit as st
import pandas as pd
from .data_manager import load_json_data, save_json_data, DRIVERS_FILE
from .utils import safe_int, safe_float, format_number

def standardize_driver(driver_dict):
    """Ensure driver dict has consistent keys"""
    # Create a copy to avoid modifying the original
    driver = driver_dict.copy()
    
    # Ensure stats exists
    if 'stats' not in driver:
        driver['stats'] = {}
        
    stats = driver['stats']
    
    # Standardize key names
    if 'raceStart' in stats and 'race_start' not in stats:
        stats['race_start'] = stats.pop('raceStart')
    elif 'race_start' in stats and 'raceStart' not in stats:
        stats['raceStart'] = stats['race_start']
        
    if 'tyreMgmt' in stats and 'tyre_mgmt' not in stats:
        stats['tyre_mgmt'] = stats.pop('tyreMgmt')
    elif 'tyre_mgmt' in stats and 'tyreMgmt' not in stats:
        stats['tyreMgmt'] = stats['tyre_mgmt']
    
    return driver

def manage_drivers():
    """Function to manage driver data and statistics"""
    st.header("Driver Management")
    
    # Load driver data
    driver_data = load_json_data(DRIVERS_FILE)
    if not driver_data:
        st.error("Failed to load driver data")
        return
    
    # Add CSV import/export functionality
    st.subheader("Import/Export CSV")
    
    # Create columns for the import/export functionality
    csv_col1, csv_col2 = st.columns(2)
    
    with csv_col1:
        st.write("Export drivers data to CSV for editing in Excel/spreadsheet:")
        if st.button("Export Drivers to CSV"):
            try:
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
                    "Race Start": d["stats"].get("raceStart", d["stats"].get("race_start", 0)),
                    "Tyre Mgmt": d["stats"].get("tyreMgmt", d["stats"].get("tyre_mgmt", 0))
                } for d in driver_data["drivers"]])
                
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
            except Exception as e:
                st.error(f"Error exporting drivers data: {e}")
    
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
                    driver_lookup = {f"{d['name']}_{d['rarity']}": d for d in driver_data["drivers"]}
                    updates_made = 0
                    
                    # Update the JSON data with values from the CSV
                    for _, row in import_df.iterrows():
                        lookup_key = f"{row['Name']}_{row['Rarity']}"
                        
                        if lookup_key in driver_lookup:
                            driver = driver_lookup[lookup_key]
                            driver_idx = driver_data["drivers"].index(driver)
                            
                            # Update all fields from the CSV using safe conversion functions
                            driver_data["drivers"][driver_idx]["level"] = safe_int(row["Level"])
                            driver_data["drivers"][driver_idx]["highestLevel"] = safe_int(row["Max Level"])
                            driver_data["drivers"][driver_idx]["upgradeInfo"]["cardsOwned"] = safe_int(row["Cards"])
                            driver_data["drivers"][driver_idx]["upgradeInfo"]["cardsNeeded"] = safe_int(row["Cards Needed"])
                            driver_data["drivers"][driver_idx]["upgradeInfo"]["coinsNeeded"] = safe_int(row["Coins Needed"])
                            driver_data["drivers"][driver_idx]["totalValue"] = safe_int(row["Total Value"])
                            driver_data["drivers"][driver_idx]["series"] = safe_int(row["Series"])
                            driver_data["drivers"][driver_idx]["inInventory"] = bool(row["In Inventory"])
                            
                            # Update stats - use consistent key names
                            driver_data["drivers"][driver_idx]["stats"]["overtaking"] = safe_int(row["Overtaking"])
                            driver_data["drivers"][driver_idx]["stats"]["defending"] = safe_int(row["Defending"])
                            driver_data["drivers"][driver_idx]["stats"]["qualifying"] = safe_int(row["Qualifying"])
                            driver_data["drivers"][driver_idx]["stats"]["raceStart"] = safe_int(row["Race Start"])
                            driver_data["drivers"][driver_idx]["stats"]["race_start"] = safe_int(row["Race Start"])
                            driver_data["drivers"][driver_idx]["stats"]["tyreMgmt"] = safe_int(row["Tyre Mgmt"])
                            driver_data["drivers"][driver_idx]["stats"]["tyre_mgmt"] = safe_int(row["Tyre Mgmt"])
                            
                            # Standardize the driver
                            driver_data["drivers"][driver_idx] = standardize_driver(driver_data["drivers"][driver_idx])
                            
                            updates_made += 1
                    
                    # Save the updated data
                    if updates_made > 0:
                        if save_json_data(driver_data, DRIVERS_FILE):
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
        "Level": int(d["level"]),
        "Max Level": int(d["highestLevel"]),
        "Cards": int(d["upgradeInfo"]["cardsOwned"]),
        "Total Value": int(d["totalValue"]),
        "Series": int(d["series"]),
        "In Inventory": bool(d["inInventory"]),
        "Overtaking": int(d["stats"]["overtaking"]),
        "Defending": int(d["stats"]["defending"]),
        "Qualifying": int(d["stats"]["qualifying"]),
        "Race Start": int(d["stats"].get("raceStart", d["stats"].get("race_start", 0))),
        "Tyre Mgmt": int(d["stats"].get("tyreMgmt", d["stats"].get("tyre_mgmt", 0)))
    } for d in driver_data["drivers"]])
    
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