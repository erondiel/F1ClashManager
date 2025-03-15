import os
import json
import pandas as pd
from src.utils.utils import update_item_upgrade_info
from src.utils.config import config, DRIVERS_FILE, COMPONENT_FILE

def import_input_tracker_csv(csv_file_path):
    """
    Import data from an Input Tracker CSV file and update JSON files.
    
    Args:
        csv_file_path (str): Path to the CSV file
        
    Returns:
        tuple: (success, message)
    """
    try:
        # Check if file exists
        if not os.path.exists(csv_file_path):
            return False, f"File not found: {csv_file_path}"
        
        # Read the CSV file
        df = pd.read_csv(csv_file_path)
        
        # Check if it's a valid Input Tracker CSV
        required_columns = ["Name", "Rarity", "Level", "Cards Owned"]
        if not all(col in df.columns for col in required_columns):
            return False, "Invalid CSV format. Missing required columns."
        
        # Process drivers section
        drivers_success, drivers_message = process_drivers_from_csv(df)
        
        # Process components section
        components_success, components_message = process_components_from_csv(df)
        
        if drivers_success and components_success:
            return True, "Successfully imported data from Input Tracker CSV."
        elif drivers_success:
            return True, f"Drivers imported successfully. Components error: {components_message}"
        elif components_success:
            return True, f"Components imported successfully. Drivers error: {drivers_message}"
        else:
            return False, f"Failed to import data. Drivers: {drivers_message}, Components: {components_message}"
            
    except Exception as e:
        return False, f"Error importing data: {str(e)}"

def process_drivers_from_csv(df):
    """
    Process drivers section from the CSV and update drivers.json
    
    Args:
        df (DataFrame): Pandas DataFrame with driver data
        
    Returns:
        tuple: (success, message)
    """
    try:
        # Filter for driver rows
        driver_df = df[df["Type"] == "Driver"].copy()
        
        if driver_df.empty:
            return False, "No driver data found in CSV."
        
        # Load existing drivers data
        drivers_data = config.load_json_data(DRIVERS_FILE)
        if not drivers_data:
            drivers_data = {"drivers": []}
        
        drivers = drivers_data.get("drivers", [])
        
        # Track updates
        updates_made = 0
        
        # Process each driver in the CSV
        for _, row in driver_df.iterrows():
            driver_name = row["Name"]
            
            # Find the driver in the existing data
            driver_found = False
            for driver in drivers:
                if driver["name"] == driver_name:
                    driver_found = True
                    
                    # Update driver data
                    driver["level"] = int(row["Level"])
                    driver["rarity"] = row["Rarity"]
                    driver["inInventory"] = True
                    
                    # Update upgrade info
                    cards_owned = int(row["Cards Owned"])
                    update_item_upgrade_info(driver, cards_owned)
                    
                    updates_made += 1
                    break
            
            if not driver_found:
                # Add new driver
                new_driver = {
                    "name": driver_name,
                    "level": int(row["Level"]),
                    "rarity": row["Rarity"],
                    "inInventory": True,
                    "upgradeInfo": {
                        "cardsOwned": int(row["Cards Owned"]),
                        "cardsNeeded": 0,  # Will be calculated by update_item_upgrade_info
                        "totalCards": 0,   # Will be calculated by update_item_upgrade_info
                    }
                }
                
                # Update upgrade info
                cards_owned = int(row["Cards Owned"])
                update_item_upgrade_info(new_driver, cards_owned)
                
                drivers.append(new_driver)
                updates_made += 1
        
        # Save the updated data
        if updates_made > 0:
            drivers_data["drivers"] = drivers
            if config.save_json_data(DRIVERS_FILE, drivers_data):
                return True, f"Successfully updated {updates_made} drivers from CSV"
            else:
                return False, "Failed to save drivers data"
        else:
            return False, "No driver updates were made"
            
    except Exception as e:
        return False, f"Error processing drivers: {str(e)}"

def process_components_from_csv(df):
    """
    Process components section from the CSV and update component JSON files
    
    Args:
        df (DataFrame): Pandas DataFrame with component data
        
    Returns:
        tuple: (success, message)
    """
    try:
        # Filter for component rows
        component_df = df[df["Type"] != "Driver"].copy()
        
        if component_df.empty:
            return False, "No component data found in CSV."
        
        # Load existing component data
        component_data = config.load_json_data(COMPONENT_FILE)
        if not component_data:
            component_data = {
                "brakes": [],
                "gearbox": [],
                "rear_wing": [],
                "front_wing": [],
                "suspension": [],
                "engine": []
            }
        
        # Map component types to their keys in the component_data dictionary
        component_type_map = {
            "Brakes": "brakes",
            "Gearbox": "gearbox",
            "Rear Wing": "rear_wing",
            "Front Wing": "front_wing",
            "Suspension": "suspension",
            "Engine": "engine"
        }
        
        # Track updates
        updates_made = 0
        
        # Process each component in the CSV
        for _, row in component_df.iterrows():
            component_name = row["Name"]
            component_type = row["Type"]
            
            # Skip if component type is not recognized
            if component_type not in component_type_map:
                continue
            
            component_key = component_type_map[component_type]
            components = component_data.get(component_key, [])
            
            # Find the component in the existing data
            component_found = False
            for component in components:
                if component["name"] == component_name:
                    component_found = True
                    
                    # Update component data
                    component["level"] = int(row["Level"])
                    component["rarity"] = row["Rarity"]
                    component["inInventory"] = True
                    
                    # Update upgrade info
                    cards_owned = int(row["Cards Owned"])
                    update_item_upgrade_info(component, cards_owned)
                    
                    updates_made += 1
                    break
            
            if not component_found:
                # Add new component
                new_component = {
                    "name": component_name,
                    "level": int(row["Level"]),
                    "rarity": row["Rarity"],
                    "inInventory": True,
                    "upgradeInfo": {
                        "cardsOwned": int(row["Cards Owned"]),
                        "cardsNeeded": 0,  # Will be calculated by update_item_upgrade_info
                        "totalCards": 0,   # Will be calculated by update_item_upgrade_info
                    }
                }
                
                # Update upgrade info
                cards_owned = int(row["Cards Owned"])
                update_item_upgrade_info(new_component, cards_owned)
                
                components.append(new_component)
                updates_made += 1
            
            # Update the components list in the component_data
            component_data[component_key] = components
        
        # Save the updated data
        if updates_made > 0:
            if config.save_json_data(COMPONENT_FILE, component_data):
                return True, f"Successfully updated {updates_made} components from CSV"
            else:
                return False, "Failed to save component data"
        else:
            return False, "No component updates were made"
            
    except Exception as e:
        return False, f"Error processing components: {str(e)}" 