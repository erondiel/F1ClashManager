import streamlit as st
import pandas as pd
import os
from src.utils.config import config, DRIVERS_FILE, COMPONENT_FILE
from .data_importer import import_input_tracker_csv

def import_special_csv_formats():
    """
    Function to import data from special CSV formats.
    Currently only supports Data Input Tracker CSV.
    """
    st.header("Import Tools")
    st.write("Import data from CSV files to update your game information")
    
    # Import Data Input & Tracker CSV
    st.subheader("Import Data from Input & Tracker CSV")
    st.write("This imports data from the Input & Tracker tab of the F1 Clash Resource Sheet.")
    st.write("The application will automatically calculate the highest possible level for each item based on cards owned.")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose your Data Input & Tracker CSV file",
        type=["csv"],
        key="tracker_data_uploader"
    )
    
    if uploaded_file is not None:
        try:
            # Save uploaded file temporarily
            temp_file_path = os.path.join("temp_uploads", "tracker_data.csv")
            os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
            
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            # Preview the file
            df = pd.read_csv(temp_file_path)
            st.write("Preview of the data:")
            st.dataframe(df.head(10))
            
            # Process the file when button is clicked
            if st.button("Import Data and Calculate Highest Levels", key="import_btn"):
                success, message = import_input_tracker_csv(temp_file_path)
                
                if success:
                    st.success(message)
                    
                    # Show sample of updated data
                    st.subheader("Updated Driver Data (Sample)")
                    drivers_data = load_json_data(DRIVERS_FILE)
                    if drivers_data and "drivers" in drivers_data:
                        # Create a DataFrame with the updated data
                        driver_rows = []
                        for driver in drivers_data["drivers"][:10]:  # Show first 10 drivers
                            if "upgradeInfo" in driver:
                                driver_rows.append({
                                    "Name": driver["name"],
                                    "Rarity": driver["rarity"],
                                    "Current Level": driver["level"],
                                    "Highest Level": driver["highestLevel"],
                                    "Cards Owned": driver["upgradeInfo"].get("cardsOwned", 0),
                                    "Cards Needed": driver["upgradeInfo"].get("cardsNeeded", 0),
                                    "Total Cards": driver["upgradeInfo"].get("totalCards", 0)
                                })
                        
                        if driver_rows:
                            st.dataframe(pd.DataFrame(driver_rows))
                else:
                    st.error(message)
            
            # Clean up
            try:
                os.remove(temp_file_path)
            except:
                pass
                
        except Exception as e:
            st.error(f"Error importing data: {str(e)}")
            st.exception(e)
    
    # Add information about the raw data processing
    st.markdown("---")
    st.subheader("Raw Data Processing")
    st.write("""
    This tool also supports calculating stats for any level using raw data files. 
    
    To generate the raw data JSON files, run the following command from the terminal:
    ```
    python generate_raw_data.py
    ```
    
    This needs to be done only once, as the game's raw stat data rarely changes.
    """) 