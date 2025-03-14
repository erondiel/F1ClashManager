import os
import shutil
import pandas as pd
import sys

def setup_data_directory():
    """Create data directory if it doesn't exist"""
    if not os.path.exists("data"):
        os.makedirs("data", exist_ok=True)
        print("Created data directory")

def process_horizontal_csv(driver_data, component_data):
    """Process and save the driver and component data from CSV strings"""
    setup_data_directory()
    
    # Path for driver data
    driver_file = "data/F1 Clash 2024 Resourse Sheet 1.7 by TR The Flash - Drivers Horizontal.csv"
    # Path for component data
    component_file = "data/F1 Clash 2024 Resourse Sheet 1.7 by TR The Flash - Components Horizontal.csv"
    
    # Save driver data to CSV
    with open(driver_file, "w") as f:
        f.write(driver_data)
    print(f"Saved driver data to {driver_file}")
    
    # Save component data to CSV
    with open(component_file, "w") as f:
        f.write(component_data)
    print(f"Saved component data to {component_file}")
    
    # Verify the files were created and are readable
    try:
        # Try to read the first few lines of each file to verify they're valid CSVs
        pd.read_csv(driver_file, nrows=5)
        pd.read_csv(component_file, nrows=5)
        print("\nVerification successful: Data files have been created and are readable.")
        print("You can now run the analysis with: python run_analysis.py")
    except Exception as e:
        print(f"\nWarning: Data files may not be valid CSV format. Error: {str(e)}")
        print("You may need to manually check the files.")

def find_and_copy_csvs():
    """Look for existing CSV files in the current directory and copy them"""
    setup_data_directory()
    found_files = False
    
    # Look for driver and component files
    for file in os.listdir():
        if file.endswith(".csv"):
            if "Driver" in file or "driver" in file:
                dest_path = "data/F1 Clash 2024 Resourse Sheet 1.7 by TR The Flash - Drivers Horizontal.csv"
                shutil.copy(file, dest_path)
                print(f"Copied {file} to {dest_path}")
                found_files = True
            elif "Compon" in file or "compon" in file:
                dest_path = "data/F1 Clash 2024 Resourse Sheet 1.7 by TR The Flash - Components Horizontal.csv"
                shutil.copy(file, dest_path)
                print(f"Copied {file} to {dest_path}")
                found_files = True
    
    return found_files

def interactive_setup():
    """Interactive setup to guide the user through setting up their data"""
    print("=" * 50)
    print("F1 Clash Data Setup Wizard")
    print("=" * 50)
    print("\nThis tool will help you set up your F1 Clash data for analysis.")
    
    # First look for CSV files in the current directory
    print("\nLooking for CSV files in the current directory...")
    found_files = find_and_copy_csvs()
    
    if found_files:
        print("\nFound and copied CSV files.")
        print("You can now run the analysis with: python run_analysis.py")
        return
    
    # If no files found, prompt user for options
    print("\nNo suitable CSV files found automatically.")
    print("\nPlease select an option:")
    print("1. I have the CSV files in another location")
    print("2. I need to export the data from the F1 Clash Resource Sheet")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ")
    
    if choice == "1":
        file_path = input("\nEnter the full path to your CSV file directory: ")
        if os.path.exists(file_path):
            for file in os.listdir(file_path):
                if file.endswith(".csv"):
                    if "Driver" in file or "driver" in file:
                        dest_path = "data/F1 Clash 2024 Resourse Sheet 1.7 by TR The Flash - Drivers Horizontal.csv"
                        shutil.copy(os.path.join(file_path, file), dest_path)
                        print(f"Copied {file} to {dest_path}")
                    elif "Compon" in file or "compon" in file:
                        dest_path = "data/F1 Clash 2024 Resourse Sheet 1.7 by TR The Flash - Components Horizontal.csv"
                        shutil.copy(os.path.join(file_path, file), dest_path)
                        print(f"Copied {file} to {dest_path}")
            print("\nFiles copied. You can now run the analysis with: python run_analysis.py")
        else:
            print(f"Error: Directory {file_path} does not exist.")
    
    elif choice == "2":
        print("\nTo export data from the F1 Clash Resource Sheet:")
        print("1. Open the Excel file in Excel or Google Sheets")
        print("2. Go to the 'Drivers Horizontal' sheet")
        print("3. Select File > Export > CSV")
        print("4. Save the file and remember the location")
        print("5. Repeat for the 'Components Horizontal' sheet")
        print("\nAfter exporting, run this setup script again and select option 1.")
    
    elif choice == "3":
        print("\nExiting setup. No changes were made.")
    
    else:
        print("\nInvalid choice. Exiting setup.")

if __name__ == "__main__":
    interactive_setup() 