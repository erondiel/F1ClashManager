import streamlit as st
import pandas as pd
from .data_manager import load_json_data, save_json_data, COMPONENT_FILES
from .utils import safe_int, safe_float, format_number

def standardize_component(component_dict):
    """Ensure component dict has consistent keys and types"""
    # Create a copy to avoid modifying the original
    component = component_dict.copy()
    
    # Ensure stats exists
    if 'stats' not in component:
        component['stats'] = {}
        
    # Ensure all stats are float values
    for stat_key in ['speed', 'cornering', 'powerUnit', 'qualifying', 'pitTime']:
        if stat_key in component['stats']:
            component['stats'][stat_key] = float(component['stats'][stat_key])
    
    # Ensure level and other numeric values are integers
    for int_field in ['level', 'highestLevel', 'series']:
        if int_field in component:
            component[int_field] = int(component[int_field])
    
    # Ensure upgradeInfo exists and has proper values
    if 'upgradeInfo' not in component:
        component['upgradeInfo'] = {}
    
    for int_field in ['cardsOwned', 'cardsNeeded', 'maxCards']:
        if int_field in component['upgradeInfo']:
            component['upgradeInfo'][int_field] = int(component['upgradeInfo'][int_field])
    
    # Ensure coinsNeeded is float
    if 'coinsNeeded' in component['upgradeInfo']:
        component['upgradeInfo']['coinsNeeded'] = float(component['upgradeInfo']['coinsNeeded'])
    
    # Ensure totalValue is float
    if 'totalValue' in component:
        component['totalValue'] = float(component['totalValue'])
    
    return component

def manage_components(component_type):
    """Function to manage components of a specific type"""
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
            try:
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
            except Exception as e:
                st.error(f"Error exporting {component_type} data: {e}")
    
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
                            
                            # Standardize the component
                            components[comp_idx] = standardize_component(components[comp_idx])
                            
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
                "Level": int(comp["level"]),
                "Max Level": int(comp["highestLevel"]),
                "Speed": format_number(comp["stats"]["speed"]),
                "Cornering": format_number(comp["stats"]["cornering"]),
                "Power Unit": format_number(comp["stats"]["powerUnit"]),
                "Qualifying": format_number(comp["stats"]["qualifying"]),
                "Pit Time": f"{float(comp['stats']['pitTime']):.2f}",
                "Total Value": format_number(comp["totalValue"]),
                "Series": int(comp["series"]),
                "In Inventory": bool(comp["inInventory"])
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