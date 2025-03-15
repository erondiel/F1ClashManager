import os
import json
import pandas as pd
import numpy as np

# Define the output paths for the raw data JSON files
COMPONENT_RAW_DATA_JSON = "data/component_raw_data.json"
DRIVER_RAW_DATA_JSON = "data/driver_raw_data.json"

def process_component_raw_data(csv_file_path):
    """
    Process component raw data CSV and generate a JSON file with stats for all levels.
    
    Args:
        csv_file_path (str): Path to the component raw data CSV file
        
    Returns:
        bool: Success status
    """
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file_path)
        print(f"Successfully read component CSV file with {len(df)} rows and {len(df.columns)} columns")
        
        # Check column names and fix if needed
        column_mapping = {}
        for col in df.columns:
            if col.strip() != col:
                column_mapping[col] = col.strip()
        
        if column_mapping:
            df = df.rename(columns=column_mapping)
            print(f"Renamed columns: {column_mapping}")
        
        # Initialize the structure for the JSON file
        component_data = {}
        
        # Print unique component names for debugging
        unique_names = df['Name'].unique()
        print(f"Found {len(unique_names)} unique components")
        
        # Process each unique component
        for name in unique_names:
            print(f"Processing component: {name}")
            # Get rows for this component
            component_df = df[df['Name'] == name]
            
            # Get the first row to extract common information
            if len(component_df) == 0:
                print(f"No rows found for component {name}")
                continue
                
            first_row = component_df.iloc[0]
            
            # Create the component entry with metadata
            component_data[name] = {
                "name": name,
                "type": first_row["Type"] if "Type" in first_row and not pd.isna(first_row["Type"]) else "",
                "rarity": first_row["Rarity"] if "Rarity" in first_row and not pd.isna(first_row["Rarity"]) else "",
                "series": int(first_row["Series"]) if "Series" in first_row and not pd.isna(first_row["Series"]) else 0,
                "levels": {}
            }
            
            # Add stats for each level
            for _, row in component_df.iterrows():
                level = int(row["Level"])
                
                # Handle pit time - convert from European format (comma as decimal) to standard format
                pit_time_str = str(row["Pit Time"]) if not pd.isna(row["Pit Time"]) else "0"
                pit_time = float(pit_time_str.replace(",", "."))
                
                speed = float(row["Speed"]) if not pd.isna(row["Speed"]) else 0.0
                cornering = float(row["Cornering"]) if not pd.isna(row["Cornering"]) else 0.0
                power_unit = float(row["Power Unit"]) if not pd.isna(row["Power Unit"]) else 0.0
                qualifying = float(row["Qualifying"]) if not pd.isna(row["Qualifying"]) else 0.0
                
                # Add stats for this level
                component_data[name]["levels"][str(level)] = {
                    "level": level,
                    "speed": speed,
                    "cornering": cornering,
                    "power_unit": power_unit,
                    "qualifying": qualifying,
                    "pit_time": pit_time,
                    "total_value": speed + cornering + power_unit + qualifying + pit_time
                }
        
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(COMPONENT_RAW_DATA_JSON), exist_ok=True)
        
        # Save to JSON file
        with open(COMPONENT_RAW_DATA_JSON, 'w') as f:
            json.dump(component_data, f, indent=2)
            
        print(f"Successfully processed component raw data and saved to {COMPONENT_RAW_DATA_JSON}")
        return True
    
    except Exception as e:
        print(f"Error processing component raw data: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def process_driver_raw_data(csv_file_path):
    """
    Process driver raw data CSV and generate a JSON file with stats for all levels.
    
    Args:
        csv_file_path (str): Path to the driver raw data CSV file
        
    Returns:
        bool: Success status
    """
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file_path)
        print(f"Successfully read driver CSV file with {len(df)} rows and {len(df.columns)} columns")
        
        # Check column names and fix if needed
        column_mapping = {}
        for col in df.columns:
            if col.strip() != col:
                column_mapping[col] = col.strip()
        
        if column_mapping:
            df = df.rename(columns=column_mapping)
            print(f"Renamed columns: {column_mapping}")
        
        # Print out a sample row for debugging
        print("First row sample:")
        first_row = df.iloc[0]
        for col in df.columns:
            print(f"  {col}: {first_row[col]} (type: {type(first_row[col])})")
        
        # Initialize the structure for the JSON file
        driver_data = {}
        
        # Print unique driver names for debugging
        unique_drivers = df['Driver'].unique()
        print(f"Found {len(unique_drivers)} unique drivers")
        
        # Process each unique driver
        for name in unique_drivers:
            print(f"Processing driver: {name}")
            # Get rows for this driver
            driver_df = df[df['Driver'] == name]
            
            # Process each rarity for this driver
            for rarity in driver_df['Rarity'].unique():
                print(f"  Processing rarity: {rarity}")
                # Get rows for this driver and rarity
                driver_rarity_df = driver_df[driver_df['Rarity'] == rarity]
                
                # Get the first row to extract common information
                if len(driver_rarity_df) == 0:
                    print(f"  No rows found for driver {name} with rarity {rarity}")
                    continue
                    
                first_row = driver_rarity_df.iloc[0]
                
                # Extract series with proper error handling
                try:
                    series = int(first_row["Series"]) if not pd.isna(first_row["Series"]) else 0
                except (ValueError, TypeError):
                    print(f"  Warning: Could not convert Series value '{first_row['Series']}' to int for {name}. Using default of 0.")
                    series = 0
                
                # Create a unique key for this driver-rarity combination
                key = f"{name}_{rarity}"
                
                # Create the driver entry with metadata
                driver_data[key] = {
                    "name": name,
                    "rarity": rarity,
                    "series": series,
                    "levels": {}
                }
                
                # Add stats for each level
                for _, row in driver_rarity_df.iterrows():
                    # Skip rows with NaN or invalid level
                    try:
                        if pd.isna(row["Level"]):
                            print(f"  Skipping row with NaN level for {name} {rarity}")
                            continue
                        level = int(row["Level"])
                    except (ValueError, TypeError):
                        print(f"  Warning: Could not convert Level value '{row['Level']}' to int for {name}. Skipping row.")
                        continue
                    
                    # Safely convert stats to integers
                    try:
                        overtaking = int(row["Overtaking"]) if not pd.isna(row["Overtaking"]) else 0
                    except (ValueError, TypeError):
                        print(f"  Warning: Could not convert Overtaking value '{row['Overtaking']}' to int for {name} level {level}")
                        overtaking = 0
                        
                    try:
                        defending = int(row["Defending"]) if not pd.isna(row["Defending"]) else 0
                    except (ValueError, TypeError):
                        print(f"  Warning: Could not convert Defending value '{row['Defending']}' to int for {name} level {level}")
                        defending = 0
                        
                    try:
                        qualifying = int(row["Qualifying"]) if not pd.isna(row["Qualifying"]) else 0
                    except (ValueError, TypeError):
                        print(f"  Warning: Could not convert Qualifying value '{row['Qualifying']}' to int for {name} level {level}")
                        qualifying = 0
                        
                    try:
                        race_start = int(row["Race Start"]) if not pd.isna(row["Race Start"]) else 0
                    except (ValueError, TypeError):
                        print(f"  Warning: Could not convert Race Start value '{row['Race Start']}' to int for {name} level {level}")
                        race_start = 0
                        
                    try:
                        tyre_mgmt = int(row["Tyre Mgmt"]) if not pd.isna(row["Tyre Mgmt"]) else 0
                    except (ValueError, TypeError):
                        print(f"  Warning: Could not convert Tyre Mgmt value '{row['Tyre Mgmt']}' to int for {name} level {level}")
                        tyre_mgmt = 0
                    
                    # Add stats for this level
                    driver_data[key]["levels"][str(level)] = {
                        "level": level,
                        "overtaking": overtaking,
                        "defending": defending,
                        "qualifying": qualifying,
                        "race_start": race_start,
                        "tyre_mgmt": tyre_mgmt,
                        "total_value": overtaking + defending + qualifying + race_start + tyre_mgmt
                    }
        
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(DRIVER_RAW_DATA_JSON), exist_ok=True)
        
        # Save to JSON file
        with open(DRIVER_RAW_DATA_JSON, 'w') as f:
            json.dump(driver_data, f, indent=2)
            
        print(f"Successfully processed driver raw data and saved to {DRIVER_RAW_DATA_JSON}")
        return True
    
    except Exception as e:
        print(f"Error processing driver raw data: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def generate_raw_data_json_files(component_csv_path, driver_csv_path):
    """
    Process the raw data CSV files and generate JSON files.
    
    Args:
        component_csv_path (str): Path to the component raw data CSV file
        driver_csv_path (str): Path to the driver raw data CSV file
        
    Returns:
        bool: Success status
    """
    print("Starting generate_raw_data_json_files function")
    
    print(f"Processing component data from: {component_csv_path}")
    component_success = process_component_raw_data(component_csv_path)
    
    print(f"Component processing result: {component_success}")
    
    if not component_success:
        print("Skipping driver processing due to component processing failure")
        return False
    
    print(f"Processing driver data from: {driver_csv_path}")
    driver_success = process_driver_raw_data(driver_csv_path)
    
    print(f"Driver processing result: {driver_success}")
    
    final_result = component_success and driver_success
    print(f"Final result: {final_result}")
    
    return final_result

def get_component_stats(component_name, level, interpolate=True):
    """
    Get component stats for a specific level.
    If the level's stats are not available in the raw data, interpolate from closest levels.
    
    Args:
        component_name (str): The name of the component
        level (int): The level to get stats for
        interpolate (bool): Whether to interpolate stats if the exact level is not found
        
    Returns:
        dict: Component stats for the requested level
    """
    try:
        # Load the raw data
        with open(COMPONENT_RAW_DATA_JSON, 'r') as f:
            raw_data = json.load(f)
        
        # Check if the component exists
        if component_name not in raw_data:
            return None
        
        component = raw_data[component_name]
        levels = component["levels"]
        
        # Check if the exact level exists
        if str(level) in levels:
            return levels[str(level)]
        
        # If not found and interpolation is enabled, interpolate from closest levels
        if interpolate:
            # Convert level keys to integers for sorting
            level_numbers = [int(l) for l in levels.keys()]
            level_numbers.sort()
            
            # Find the closest lower and higher levels
            lower_level = None
            higher_level = None
            
            for l in level_numbers:
                if l < level:
                    lower_level = l
                elif l > level:
                    higher_level = l
                    break
            
            # If we have both lower and higher levels, interpolate
            if lower_level is not None and higher_level is not None:
                lower_stats = levels[str(lower_level)]
                higher_stats = levels[str(higher_level)]
                
                # Calculate the interpolation factor
                factor = (level - lower_level) / (higher_level - lower_level)
                
                # Interpolate each stat
                interpolated_stats = {
                    "level": level,
                    "speed": lower_stats["speed"] + factor * (higher_stats["speed"] - lower_stats["speed"]),
                    "cornering": lower_stats["cornering"] + factor * (higher_stats["cornering"] - lower_stats["cornering"]),
                    "power_unit": lower_stats["power_unit"] + factor * (higher_stats["power_unit"] - lower_stats["power_unit"]),
                    "qualifying": lower_stats["qualifying"] + factor * (higher_stats["qualifying"] - lower_stats["qualifying"]),
                    "pit_time": lower_stats["pit_time"] + factor * (higher_stats["pit_time"] - lower_stats["pit_time"])
                }
                
                # Calculate total value
                interpolated_stats["total_value"] = (
                    interpolated_stats["speed"] + 
                    interpolated_stats["cornering"] + 
                    interpolated_stats["power_unit"] + 
                    interpolated_stats["qualifying"] + 
                    interpolated_stats["pit_time"]
                )
                
                return interpolated_stats
            
            # If we only have lower level, use that
            elif lower_level is not None:
                return levels[str(lower_level)]
            
            # If we only have higher level, use that
            elif higher_level is not None:
                return levels[str(higher_level)]
        
        # If level not found and interpolation fails or is disabled
        return None
    
    except Exception as e:
        print(f"Error getting component stats: {str(e)}")
        return None

def get_driver_stats(driver_name, rarity, level, interpolate=True):
    """
    Get driver stats for a specific level.
    If the level's stats are not available in the raw data, interpolate from closest levels.
    
    Args:
        driver_name (str): The name of the driver
        rarity (str): The rarity of the driver
        level (int): The level to get stats for
        interpolate (bool): Whether to interpolate stats if the exact level is not found
        
    Returns:
        dict: Driver stats for the requested level
    """
    try:
        # Load the raw data
        with open(DRIVER_RAW_DATA_JSON, 'r') as f:
            raw_data = json.load(f)
        
        # Create the key for this driver-rarity combination
        key = f"{driver_name}_{rarity}"
        
        # Check if the driver exists
        if key not in raw_data:
            return None
        
        driver = raw_data[key]
        levels = driver["levels"]
        
        # Check if the exact level exists
        if str(level) in levels:
            return levels[str(level)]
        
        # If not found and interpolation is enabled, interpolate from closest levels
        if interpolate:
            # Convert level keys to integers for sorting
            level_numbers = [int(l) for l in levels.keys()]
            level_numbers.sort()
            
            # Find the closest lower and higher levels
            lower_level = None
            higher_level = None
            
            for l in level_numbers:
                if l < level:
                    lower_level = l
                elif l > level:
                    higher_level = l
                    break
            
            # If we have both lower and higher levels, interpolate
            if lower_level is not None and higher_level is not None:
                lower_stats = levels[str(lower_level)]
                higher_stats = levels[str(higher_level)]
                
                # Calculate the interpolation factor
                factor = (level - lower_level) / (higher_level - lower_level)
                
                # Interpolate each stat
                interpolated_stats = {
                    "level": level,
                    "overtaking": round(lower_stats["overtaking"] + factor * (higher_stats["overtaking"] - lower_stats["overtaking"])),
                    "defending": round(lower_stats["defending"] + factor * (higher_stats["defending"] - lower_stats["defending"])),
                    "qualifying": round(lower_stats["qualifying"] + factor * (higher_stats["qualifying"] - lower_stats["qualifying"])),
                    "race_start": round(lower_stats["race_start"] + factor * (higher_stats["race_start"] - lower_stats["race_start"])),
                    "tyre_mgmt": round(lower_stats["tyre_mgmt"] + factor * (higher_stats["tyre_mgmt"] - lower_stats["tyre_mgmt"]))
                }
                
                # Calculate total value
                interpolated_stats["total_value"] = (
                    interpolated_stats["overtaking"] + 
                    interpolated_stats["defending"] + 
                    interpolated_stats["qualifying"] + 
                    interpolated_stats["race_start"] + 
                    interpolated_stats["tyre_mgmt"]
                )
                
                return interpolated_stats
            
            # If we only have lower level, use that
            elif lower_level is not None:
                return levels[str(lower_level)]
            
            # If we only have higher level, use that
            elif higher_level is not None:
                return levels[str(higher_level)]
        
        # If level not found and interpolation fails or is disabled
        return None
    
    except Exception as e:
        print(f"Error getting driver stats: {str(e)}")
        return None 