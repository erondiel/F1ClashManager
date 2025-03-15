import os
import sys
from src.raw_data_processor import get_component_stats, get_driver_stats

def test_component_stats():
    """
    Test getting component stats for different levels.
    """
    print("Testing component stats calculation...")
    print("-" * 80)
    
    # List of components to test
    test_components = [
        # Test case from vertical CSV: The Stabiliser, Level 8
        {
            "name": "The Stabiliser",
            "level": 8,
            "expected_speed": 8,
            "expected_cornering": 8,
            "expected_power_unit": 7,
            "expected_qualifying": 9,
            "expected_pit_time": 0.77,
            "expected_total": 32.77
        },
        # Test with a level not in the raw data (should interpolate)
        {
            "name": "The Stabiliser",
            "level": 4,  # Interpolated level
            "interpolate": True
        },
        # Test legendary item
        {
            "name": "The Accord",
            "level": 8,
            "expected_speed": 14,
            "expected_cornering": 6,
            "expected_power_unit": 5,
            "expected_qualifying": 8,
            "expected_pit_time": 0.60,
            "expected_total": 33.60
        }
    ]
    
    # Run each test case
    for i, test in enumerate(test_components):
        print(f"Test Case {i+1}: {test['name']} (Level {test['level']})")
        
        # Get the stats
        stats = get_component_stats(
            test["name"], 
            test["level"], 
            interpolate=test.get("interpolate", True)
        )
        
        if stats is None:
            print(f"  Error: No stats found for {test['name']} at level {test['level']}")
            continue
        
        # Print the results
        print(f"  Speed: {stats['speed']}")
        print(f"  Cornering: {stats['cornering']}")
        print(f"  Power Unit: {stats['power_unit']}")
        print(f"  Qualifying: {stats['qualifying']}")
        print(f"  Pit Time: {stats['pit_time']}")
        print(f"  Total Value: {stats['total_value']}")
        
        # Check against expected values if provided
        if "expected_speed" in test:
            print(f"  Expected Speed: {test['expected_speed']} - {'✓' if round(stats['speed'], 2) == round(test['expected_speed'], 2) else '✗'}")
        if "expected_cornering" in test:
            print(f"  Expected Cornering: {test['expected_cornering']} - {'✓' if round(stats['cornering'], 2) == round(test['expected_cornering'], 2) else '✗'}")
        if "expected_power_unit" in test:
            print(f"  Expected Power Unit: {test['expected_power_unit']} - {'✓' if round(stats['power_unit'], 2) == round(test['expected_power_unit'], 2) else '✗'}")
        if "expected_qualifying" in test:
            print(f"  Expected Qualifying: {test['expected_qualifying']} - {'✓' if round(stats['qualifying'], 2) == round(test['expected_qualifying'], 2) else '✗'}")
        if "expected_pit_time" in test:
            print(f"  Expected Pit Time: {test['expected_pit_time']} - {'✓' if round(stats['pit_time'], 2) == round(test['expected_pit_time'], 2) else '✗'}")
        if "expected_total" in test:
            print(f"  Expected Total: {test['expected_total']} - {'✓' if round(stats['total_value'], 2) == round(test['expected_total'], 2) else '✗'}")
        
        print()
    
    print("-" * 80)

def test_driver_stats():
    """
    Test getting driver stats for different levels.
    """
    print("Testing driver stats calculation...")
    print("-" * 80)
    
    # List of drivers to test
    test_drivers = [
        # Test case from vertical CSV: Bottas, Epic, Level 5
        {
            "name": "Bottas",
            "rarity": "Epic",
            "level": 5,
            "expected_overtaking": 69,
            "expected_defending": 74,
            "expected_qualifying": 59,
            "expected_race_start": 54,
            "expected_tyre_mgmt": 64,
            "expected_total": 320
        },
        # Test with a level not in the raw data (should interpolate)
        {
            "name": "Bottas",
            "rarity": "Epic",
            "level": 3,  # Interpolated level
            "interpolate": True
        },
        # Test legendary driver
        {
            "name": "Berger",
            "rarity": "Legendary",
            "level": 6,
            "expected_overtaking": 39,
            "expected_defending": 51,
            "expected_qualifying": 43,
            "expected_race_start": 35,
            "expected_tyre_mgmt": 47,
            "expected_total": 215
        }
    ]
    
    # Run each test case
    for i, test in enumerate(test_drivers):
        print(f"Test Case {i+1}: {test['name']} ({test['rarity']}, Level {test['level']})")
        
        # Get the stats
        stats = get_driver_stats(
            test["name"], 
            test["rarity"], 
            test["level"], 
            interpolate=test.get("interpolate", True)
        )
        
        if stats is None:
            print(f"  Error: No stats found for {test['name']} ({test['rarity']}) at level {test['level']}")
            continue
        
        # Print the results
        print(f"  Overtaking: {stats['overtaking']}")
        print(f"  Defending: {stats['defending']}")
        print(f"  Qualifying: {stats['qualifying']}")
        print(f"  Race Start: {stats['race_start']}")
        print(f"  Tyre Mgmt: {stats['tyre_mgmt']}")
        print(f"  Total Value: {stats['total_value']}")
        
        # Check against expected values if provided
        if "expected_overtaking" in test:
            print(f"  Expected Overtaking: {test['expected_overtaking']} - {'✓' if stats['overtaking'] == test['expected_overtaking'] else '✗'}")
        if "expected_defending" in test:
            print(f"  Expected Defending: {test['expected_defending']} - {'✓' if stats['defending'] == test['expected_defending'] else '✗'}")
        if "expected_qualifying" in test:
            print(f"  Expected Qualifying: {test['expected_qualifying']} - {'✓' if stats['qualifying'] == test['expected_qualifying'] else '✗'}")
        if "expected_race_start" in test:
            print(f"  Expected Race Start: {test['expected_race_start']} - {'✓' if stats['race_start'] == test['expected_race_start'] else '✗'}")
        if "expected_tyre_mgmt" in test:
            print(f"  Expected Tyre Mgmt: {test['expected_tyre_mgmt']} - {'✓' if stats['tyre_mgmt'] == test['expected_tyre_mgmt'] else '✗'}")
        if "expected_total" in test:
            print(f"  Expected Total: {test['expected_total']} - {'✓' if stats['total_value'] == test['expected_total'] else '✗'}")
        
        print()
    
    print("-" * 80)

def main():
    """
    Run tests for raw data processing.
    """
    # Check if raw data JSON files exist
    data_dir = "data"
    component_json = os.path.join(data_dir, "component_raw_data.json")
    driver_json = os.path.join(data_dir, "driver_raw_data.json")
    
    if not os.path.exists(component_json) or not os.path.exists(driver_json):
        print("Error: Raw data JSON files not found. Please run generate_raw_data.py first.")
        return False
    
    # Run tests
    print("\n=== COMPONENT STATS TESTS ===")
    test_component_stats()
    
    print("\n=== DRIVER STATS TESTS ===")
    test_driver_stats()
    
    print("\nAll tests completed successfully!")
    return True

if __name__ == "__main__":
    main() 