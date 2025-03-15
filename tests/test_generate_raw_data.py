import os
import sys
import traceback
import pandas as pd
from src.raw_data_processor import process_component_raw_data, process_driver_raw_data

def inspect_csv(file_path):
    """
    Inspect a CSV file and print diagnostic information.
    """
    print(f"Inspecting CSV file: {file_path}")
    df = pd.read_csv(file_path)
    
    print(f"CSV shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    print(f"First few rows:")
    print(df.head(2))
    
    return df

def main():
    """
    Test generating raw data JSON files from CSV files.
    """
    # Paths for the CSV files
    component_csv_path = "CSV/F1 Clash 2024 Resource Sheet 1.7 - ComponentRawData.csv"
    driver_csv_path = "CSV/F1 Clash 2024 Resource Sheet 1.7 - DriverRawData.csv"
    
    # Check if the files exist
    if not os.path.exists(component_csv_path):
        print(f"Error: Component CSV file not found at {component_csv_path}")
        return False
    
    if not os.path.exists(driver_csv_path):
        print(f"Error: Driver CSV file not found at {driver_csv_path}")
        return False
    
    print(f"Found component CSV at: {component_csv_path}")
    print(f"Found driver CSV at: {driver_csv_path}")
    
    # Inspect the CSV files
    print("\n=== Component CSV Inspection ===")
    component_df = inspect_csv(component_csv_path)
    
    print("\n=== Driver CSV Inspection ===")
    driver_df = inspect_csv(driver_csv_path)
    
    # Process component data
    print("\nProcessing component data...")
    try:
        component_success = process_component_raw_data(component_csv_path)
        print(f"Component processing result: {component_success}")
    except Exception as e:
        print(f"Error processing component data: {str(e)}")
        traceback.print_exc()
        return False
    
    # Process driver data
    print("\nProcessing driver data...")
    try:
        driver_success = process_driver_raw_data(driver_csv_path)
        print(f"Driver processing result: {driver_success}")
    except Exception as e:
        print(f"Error processing driver data: {str(e)}")
        traceback.print_exc()
        return False
    
    return component_success and driver_success

if __name__ == "__main__":
    success = main()
    if success:
        print("Successfully generated raw data JSON files.")
    else:
        print("Failed to generate raw data JSON files.") 