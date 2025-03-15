import os
import sys
from src.raw_data_processor import generate_raw_data_json_files

def main():
    """
    Generate raw data JSON files from CSV files.
    
    Usage:
        python generate_raw_data.py [component_csv_path] [driver_csv_path]
        
    If no paths are provided, default paths will be used.
    """
    # Default paths for the CSV files
    default_component_csv = "CSV/F1 Clash 2024 Resource Sheet 1.7 - ComponentRawData.csv"
    default_driver_csv = "CSV/F1 Clash 2024 Resource Sheet 1.7 - DriverRawData.csv"
    
    # Get paths from command line arguments or use defaults
    component_csv_path = sys.argv[1] if len(sys.argv) > 1 else default_component_csv
    driver_csv_path = sys.argv[2] if len(sys.argv) > 2 else default_driver_csv
    
    # Check if the files exist
    if not os.path.exists(component_csv_path):
        print(f"Error: Component CSV file not found at {component_csv_path}")
        return False
    
    if not os.path.exists(driver_csv_path):
        print(f"Error: Driver CSV file not found at {driver_csv_path}")
        return False
    
    # Process the CSV files and generate the JSON files
    print(f"Generating raw data JSON files from:")
    print(f"  Component CSV: {component_csv_path}")
    print(f"  Driver CSV: {driver_csv_path}")
    
    success = generate_raw_data_json_files(component_csv_path, driver_csv_path)
    
    if success:
        print("Successfully generated raw data JSON files.")
    else:
        print("Failed to generate raw data JSON files.")
    
    return success

if __name__ == "__main__":
    main() 