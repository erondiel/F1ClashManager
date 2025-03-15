import csv
import json
import os
from typing import Dict, List, Any, Union

# Define file paths - updated for the new CSV structure
DATA_INPUT_TRACKER = "F1 Clash 2024 Resource Sheet 1.7 - Data Input _ Tracker.csv"
DRIVERS_VERTICAL = "F1 Clash 2024 Resource Sheet 1.7 - Drivers Vertical Combined.csv"
COMPONENTS_VERTICAL = "F1 Clash 2024 Resource Sheet 1.7 - Components Vertical.csv"
TRACK_BOOSTS = "F1 Clash 2024 Resourse Sheet 1.7 by TR The Flash - Track Boosts.csv"
SERIES_TRACK_SETUPS = "F1 Clash 2024 Resourse Sheet 1.7 by TR The Flash - Series Track Stat Setups.csv"
BOOSTS = "F1 Clash 2024 Resourse Sheet 1.7 - Boosts.csv"

# Component output files
OUTPUT_BRAKES = "components_brakes.json"
OUTPUT_GEARBOX = "components_gearbox.json"
OUTPUT_REARWING = "components_rearwing.json"
OUTPUT_FRONTWING = "components_frontwing.json"
OUTPUT_SUSPENSION = "components_suspension.json"
OUTPUT_ENGINE = "components_engine.json"

# Output files
OUTPUT_DRIVERS = "drivers.json"
OUTPUT_TRACK_BOOSTS = "track_boosts.json"
OUTPUT_SERIES_SETUPS = "series_setups.json"
OUTPUT_BOOSTS = "boosts.json"

# Define category mappings for consistency
CATEGORY_MAPPING = {
    # From tracker file
    "Brakes": "Brakes",
    "Gearbox": "Gearbox",
    "Rear Wing": "Rear Wing",
    "Front Wing": "Front Wing",
    "Suspension": "Suspension",
    "Engine": "Engine",
    # From vertical file
    "BRAKES": "Brakes",
    "GEARBOX": "Gearbox",
    "REAR WING": "Rear Wing",
    "FRONT WING": "Front Wing",
    "SUSPENSION": "Suspension",
    "ENGINE": "Engine"
}

def ensure_directory_exists(filepath: str) -> None:
    """Ensure the directory for the given filepath exists."""
    directory = os.path.dirname(filepath)
    if not os.path.exists(directory):
        os.makedirs(directory)

def extract_driver_data_from_tracker(file_path: str) -> Dict[str, Dict[str, Any]]:
    """Extract driver data from the tracker CSV, handling the modified structure."""
    driver_data = {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            rows = list(reader)
            
        # Find the row with header "Drivers"
        header_row = None
        for i, row in enumerate(rows):
            if row and row[0] == "Drivers":
                header_row = i
                break
        
        if header_row is None:
            print("Error: Could not find 'Drivers' header in tracker CSV")
            return {}
        
        # Extract column headers
        headers = rows[header_row]
        
        # Process driver data rows (starting from the next row after headers)
        for i in range(header_row + 1, len(rows)):
            row = rows[i]
            
            # Stop when we reach "Components" or the end of data
            if not row or not row[0] or row[0] == "Components":
                break
            
            driver_name = row[0].strip() if row[0] else ""
            if not driver_name:
                continue
                
            try:
                # Extract data from the modified CSV format
                rarity = row[1].strip() if len(row) > 1 and row[1] else "Common"
                level = int(row[2]) if len(row) > 2 and row[2] else 0
                highest_level = int(row[3]) if len(row) > 3 and row[3] else 0
                cards_owned = int(row[4]) if len(row) > 4 and row[4] else 0
                cards_needed = int(row[5]) if len(row) > 5 and row[5] else 0
                max_cards = int(row[6]) if len(row) > 6 and row[6] else 0
                per_level = int(row[7]) if len(row) > 7 and row[7] else 0
                total_cards = int(row[8]) if len(row) > 8 and row[8] else 0
                
                # Create a unique key for this driver
                key = f"{driver_name}_{rarity}"
                
                driver_data[key] = {
                    "name": driver_name,
                    "rarity": rarity,
                    "level": level,
                    "highestLevel": highest_level,
                    "inInventory": level > 0,
                    "upgradeInfo": {
                        "cardsOwned": cards_owned,
                        "cardsNeeded": cards_needed,
                        "maxCards": max_cards,
                        "perLevel": per_level,
                        "totalCards": total_cards,
                        "coinsNeeded": 0  # Will be updated from other data source
                    }
                }
            except Exception as e:
                print(f"Error processing driver row {i}: {e}")
        
        return driver_data
    except Exception as e:
        print(f"Error extracting driver data from tracker: {e}")
        return {}

def extract_component_data_from_tracker(file_path: str) -> Dict[str, Dict[str, Any]]:
    """Extract component data from the tracker CSV, handling the modified structure."""
    component_data = {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            rows = list(reader)
        
        # Find the "Components" row
        component_row = None
        for i, row in enumerate(rows):
            if row and row[0] == "Components":
                component_row = i
                break
        
        if component_row is None:
            print("Error: Could not find 'Components' header in tracker CSV")
            return {}
        
        # Current category being processed
        current_category = None
        
        # Process component rows
        for i in range(component_row + 1, len(rows)):
            row = rows[i]
            
            # Skip empty rows
            if not row or not row[0]:
                continue
                
            # Check if this is a category header row
            if row[0] in CATEGORY_MAPPING:
                current_category = CATEGORY_MAPPING[row[0]]
                print(f"Processing component category: {current_category}")
                continue
            
            # Skip rows until we have a category
            if not current_category:
                continue
                
            try:
                component_name = row[0].strip()
                if not component_name:
                    continue
                    
                # Extract data from the modified CSV format
                rarity = row[1].strip() if len(row) > 1 and row[1] else "Common"
                level = int(row[2]) if len(row) > 2 and row[2] else 0
                highest_level = int(row[3]) if len(row) > 3 and row[3] else 0
                cards_owned = int(row[4]) if len(row) > 4 and row[4] else 0
                cards_needed = int(row[5]) if len(row) > 5 and row[5] else 0
                max_cards = int(row[6]) if len(row) > 6 and row[6] else 0
                per_level = int(row[7]) if len(row) > 7 and row[7] else 0
                total_cards = int(row[8]) if len(row) > 8 and row[8] else 0
                
                # Create a unique key for this component
                key = f"{component_name}_{current_category}"
                
                component_data[key] = {
                    "name": component_name,
                    "category": current_category,
                    "rarity": rarity,
                    "level": level,
                    "highestLevel": highest_level,
                    "inInventory": level > 0,
                    "upgradeInfo": {
                        "cardsOwned": cards_owned,
                        "cardsNeeded": cards_needed,
                        "maxCards": max_cards,
                        "perLevel": per_level,
                        "totalCards": total_cards,
                        "coinsNeeded": 0  # Will be updated from other data source
                    }
                }
            except Exception as e:
                print(f"Error processing component row {i}: {e}")
    
        # Print summary of components by category
        categories = {}
        for key, comp in component_data.items():
            cat = comp["category"]
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1
            
        print("Components by category:")
        for cat, count in categories.items():
            print(f"  {cat}: {count} components")
        
        return component_data
    except Exception as e:
        print(f"Error extracting component data from tracker: {e}")
        return {}

def extract_driver_stats(file_path: str) -> Dict[str, Dict[str, Any]]:
    """Extract driver stats from the Drivers Vertical Combined CSV with the new format."""
    driver_stats = {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if not row.get('Drivers'):
                    continue
                    
                driver_name = row.get('Drivers', '').strip()
                rarity = row.get('Rarity', '').strip()
                
                if not driver_name or not rarity:
                    continue
                
                try:
                    level = int(row.get('Level', 0))
                    overtaking = int(row.get('Overtaking', 0))
                    defending = int(row.get('Defending', 0))
                    qualifying = int(row.get('Qualifying', 0))
                    race_start = int(row.get('Race Start', 0))
                    tyre_mgmt = int(row.get('Tyre Mgmt', 0))
                    total_value = int(row.get('Total Value', 0))
                    series = int(row.get('Series', 0))
                    
                    # Handle potential monetary values with commas
                    coins_needed = row.get('Coins', '0')
                    if coins_needed:
                        coins_needed = int(coins_needed.replace(',', '').replace('"', ''))
                    else:
                        coins_needed = 0
                except (ValueError, AttributeError) as e:
                    print(f"Error parsing driver stats for {driver_name}: {e}")
                    continue
                    
                key = f"{driver_name}_{rarity}"
                driver_stats[key] = {
                    "stats": {
                        "overtaking": overtaking,
                        "defending": defending,
                        "qualifying": qualifying,
                        "raceStart": race_start,
                        "tyreMgmt": tyre_mgmt
                    },
                    "totalValue": total_value,
                    "series": series,
                    "upgradeInfo": {
                        "coinsNeeded": coins_needed
                    }
                }
        
        print(f"Extracted stats for {len(driver_stats)} drivers")
        return driver_stats
    except Exception as e:
        print(f"Error extracting driver stats: {e}")
        return {}

def extract_component_stats(file_path: str) -> Dict[str, Dict[str, Any]]:
    """Extract component stats from the Components Vertical CSV with the new format."""
    component_stats = {}
    current_category = None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            rows = list(reader)
        
        print("Scanning Components Vertical CSV for categories...")
        
        for i, row in enumerate(rows):
            if not row or len(row) < 2:
                continue
            
            # Check if this is a category header (we check for all caps categories)
            if row[0] and row[0] in CATEGORY_MAPPING:
                current_category = CATEGORY_MAPPING[row[0]]
                print(f"Found category: {current_category}")
                continue
                
            # Skip if no category or no component name
            if not current_category or not row[1] or row[1] == "Name":
                continue
                
            component_name = row[1].strip()
            if not component_name:
                continue
            
            try:
                # Convert stats to proper numeric types - use float consistently for all stats
                level = int(row[2]) if len(row) > 2 and row[2] else 0
                
                # Make sure we consistently use float for all numeric stats
                speed = float(row[4]) if len(row) > 4 and row[4] else 0.0
                cornering = float(row[5]) if len(row) > 5 and row[5] else 0.0
                power_unit = float(row[6]) if len(row) > 6 and row[6] else 0.0
                qualifying = float(row[7]) if len(row) > 7 and row[7] else 0.0
                pit_time = float(row[8]) if len(row) > 8 and row[8] else 0.0
                
                # For consistency, make sure these are integers
                total_value = int(float(row[9])) if len(row) > 9 and row[9] else 0
                series = int(float(row[10])) if len(row) > 10 and row[10] else 0
                
                # Handle monetary values with commas
                coins_needed = row[13] if len(row) > 13 and row[13] else '0'
                if coins_needed:
                    coins_needed = int(coins_needed.replace(',', '').replace('"', ''))
                else:
                    coins_needed = 0
                    
                # Get rarity based on the component name and total value
                rarity = "Common"
                if total_value > 70:
                    rarity = "Epic"
                elif total_value > 40:
                    rarity = "Rare"
                    
                key = f"{component_name}_{current_category}"
                component_stats[key] = {
                    "category": current_category,
                    "rarity": rarity,
                    "stats": {
                        "speed": speed,  # consistently use float
                        "cornering": cornering,
                        "powerUnit": power_unit,
                        "qualifying": qualifying,
                        "pitTime": pit_time
                    },
                    "totalValue": total_value,
                    "series": series,
                    "upgradeInfo": {
                        "coinsNeeded": coins_needed
                    }
                }
            except (ValueError, IndexError) as e:
                print(f"Error processing component {component_name} in row {i}: {e}")
                continue
        
        print(f"Extracted stats for {len(component_stats)} components")
        return component_stats
    except Exception as e:
        print(f"Error extracting component stats: {e}")
        return {}

def merge_driver_data(tracker_data: Dict[str, Dict[str, Any]], stats_data: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Merge driver data from tracker and stats sources."""
    merged_drivers = []
    processed_drivers = set()
    
    print(f"Merging driver data: {len(tracker_data)} from tracker, {len(stats_data)} from stats")
    
    # First, process all drivers from tracker data
    for key, driver in tracker_data.items():
        driver_name = driver["name"]
        rarity = driver["rarity"]
        driver_key = f"{driver_name}_{rarity}"
        
        # Create a merged driver with basic info from tracker
        merged_driver = {
            "name": driver_name,
            "rarity": rarity,
            "level": driver["level"],
            "highestLevel": driver["highestLevel"],
            "inInventory": driver["inInventory"],
            "upgradeInfo": driver["upgradeInfo"],
            "stats": {
                "overtaking": 0,
                "defending": 0,
                "qualifying": 0,
                "raceStart": 0,
                "tyreMgmt": 0
            },
            "totalValue": 0,
            "series": 0
        }
        
        # If we have stats for this driver, update with those values
        if driver_key in stats_data:
            stats = stats_data[driver_key]
            merged_driver["stats"] = stats["stats"]
            merged_driver["totalValue"] = stats["totalValue"]
            merged_driver["series"] = stats["series"]
            
            # Update coins needed if available
            if stats["upgradeInfo"].get("coinsNeeded", 0) > 0:
                merged_driver["upgradeInfo"]["coinsNeeded"] = stats["upgradeInfo"]["coinsNeeded"]
        
        merged_drivers.append(merged_driver)
        processed_drivers.add(driver_key)
    
    # Add any drivers that are in stats data but not in tracker data
    for key, stats in stats_data.items():
        if key not in processed_drivers:
            driver_name, rarity = key.split('_', 1)
            
            # Create a basic driver entry from stats
            merged_driver = {
                "name": driver_name,
                "rarity": rarity,
                "level": 0,  # Default value
                "highestLevel": 0,
                "inInventory": False,
                "upgradeInfo": {
                    "cardsOwned": 0,
                    "cardsNeeded": 0,
                    "maxCards": 0,
                    "perLevel": 0,
                    "totalCards": 0,
                    "coinsNeeded": stats["upgradeInfo"].get("coinsNeeded", 0)
                },
                "stats": stats["stats"],
                "totalValue": stats["totalValue"],
                "series": stats["series"]
            }
            
            merged_drivers.append(merged_driver)
    
    # Add legacy points field to legendary drivers
    for driver in merged_drivers:
        if driver["rarity"] == "Legendary" and "legacyPoints" not in driver:
            driver["legacyPoints"] = 0
    
    # Sort by name and rarity
    merged_drivers.sort(key=lambda x: (x["name"], x["rarity"]))
    
    print(f"Merged {len(merged_drivers)} drivers in total")
    return merged_drivers

def merge_component_data(tracker_data: Dict[str, Dict[str, Any]], stats_data: Dict[str, Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Merge component data from tracker and stats sources."""
    merged_components = {}
    category_components = {
        "Brakes": [],
        "Gearbox": [],
        "Rear Wing": [],
        "Front Wing": [],
        "Suspension": [],
        "Engine": []
    }
    processed_component_names = set()
    
    print(f"Merging component data: {len(tracker_data)} from tracker, {len(stats_data)} from stats")
    
    # First, process all components from tracker data
    for key, component in tracker_data.items():
        name = component["name"]
        category = component["category"]
        rarity = component["rarity"]
        component_key = f"{name}_{category}"
        
        # Create a merged component with basic info from tracker
        merged_component = {
            "name": name,
            "category": category,
            "rarity": rarity,
            "level": component["level"],
            "highestLevel": component["highestLevel"],
            "inInventory": component["inInventory"],
            "upgradeInfo": component["upgradeInfo"],
            "stats": {
                "speed": 0.0,  # Use float for consistency
                "cornering": 0.0,
                "powerUnit": 0.0,
                "qualifying": 0.0,
                "pitTime": 0.0
            },
            "totalValue": 0,
            "series": 0
        }
        
        # If we have stats for this component, update with those values
        if component_key in stats_data:
            stats = stats_data[component_key]
            merged_component["stats"] = stats["stats"]
            merged_component["totalValue"] = stats["totalValue"]
            merged_component["series"] = stats["series"]
            
            # Update coins needed if available
            if "coinsNeeded" in stats["upgradeInfo"] and stats["upgradeInfo"]["coinsNeeded"] > 0:
                merged_component["upgradeInfo"]["coinsNeeded"] = stats["upgradeInfo"]["coinsNeeded"]
        
        # Add to the appropriate category
        if category in category_components:
            category_components[category].append(merged_component)
        
        processed_component_names.add(component_key)
    
    # Add any components that are in stats data but not in tracker data
    for key, stats in stats_data.items():
        if key not in processed_component_names:
            name, category = key.rsplit('_', 1)
            
            # Use category from stats data
            category = stats["category"]
            rarity = stats["rarity"]
            
            # Create a basic component entry from stats
            merged_component = {
                "name": name,
                "category": category,
                "rarity": rarity,
                "level": 0,  # Default value
                "highestLevel": 0,
                "inInventory": False,
                "upgradeInfo": {
                    "cardsOwned": 0,
                    "cardsNeeded": 0,
                    "maxCards": 0,
                    "perLevel": 0,
                    "totalCards": 0,
                    "coinsNeeded": stats["upgradeInfo"].get("coinsNeeded", 0)
                },
                "stats": stats["stats"],
                "totalValue": stats["totalValue"],
                "series": stats["series"]
            }
            
            # Add to the appropriate category
            if category in category_components:
                category_components[category].append(merged_component)
            
            processed_component_names.add(key)
    
    # Sort each category by total value (descending)
    for category in category_components:
        category_components[category].sort(key=lambda x: -x["totalValue"])
        print(f"Category {category} has {len(category_components[category])} components after merging")
    
    return category_components

def main():
    # Print a message to verify script execution
    print("Starting data extraction process...")
    print(f"Reading data from: {DATA_INPUT_TRACKER}, {DRIVERS_VERTICAL}, and {COMPONENTS_VERTICAL}")
    
    # Extract data from tracker CSV
    driver_tracker_data = extract_driver_data_from_tracker(DATA_INPUT_TRACKER)
    component_tracker_data = extract_component_data_from_tracker(DATA_INPUT_TRACKER)
    print(f"Extracted {len(driver_tracker_data)} drivers and {len(component_tracker_data)} components from tracker")
    
    # Extract stats from vertical CSVs
    driver_stats_data = extract_driver_stats(DRIVERS_VERTICAL)
    component_stats_data = extract_component_stats(COMPONENTS_VERTICAL)
    print(f"Extracted {len(driver_stats_data)} driver stats and {len(component_stats_data)} component stats")
    
    # Merge the data
    merged_drivers = merge_driver_data(driver_tracker_data, driver_stats_data)
    category_components = merge_component_data(component_tracker_data, component_stats_data)
    
    # Write drivers data to JSON file
    with open(OUTPUT_DRIVERS, 'w', encoding='utf-8') as file:
        json.dump({"drivers": merged_drivers}, file, indent=2)
    print(f"Drivers data saved to {OUTPUT_DRIVERS}")
    
    # Write component data to separate JSON files for each type
    component_files = {
        "Brakes": OUTPUT_BRAKES,
        "Gearbox": OUTPUT_GEARBOX,
        "Rear Wing": OUTPUT_REARWING,
        "Front Wing": OUTPUT_FRONTWING,
        "Suspension": OUTPUT_SUSPENSION,
        "Engine": OUTPUT_ENGINE
    }
    
    for category, output_file in component_files.items():
        with open(output_file, 'w', encoding='utf-8') as file:
            # Convert category to JSON key format
            json_key = category.lower().replace(" ", "_")
            
            # Count number of components in this category
            component_count = len(category_components.get(category, []))
            
            json.dump({json_key: category_components.get(category, [])}, file, indent=2)
            print(f"{category} data saved to {output_file} ({component_count} components)")
    
    print("Data extraction and conversion complete!")

if __name__ == "__main__":
    main() 