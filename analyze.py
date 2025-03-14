import os
import pandas as pd
import numpy as np
import json
from pathlib import Path

class F1ClashAnalyzer:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.drivers = {}
        self.components = {}
        self.series_limits = {}
        self.output_dir = "output"
        
        # Ensure output directory exists
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def load_data(self, drivers_file=None, components_file=None):
        """Load driver and component data from CSV files"""
        print("Loading F1 Clash data...")
        
        if drivers_file:
            self.load_drivers(drivers_file)
        
        if components_file:
            self.load_components(components_file)
            
        self.generate_summary_files()
        print("Data loading complete.")
    
    def load_drivers(self, drivers_file):
        """Parse and organize driver data"""
        print(f"Loading drivers from {drivers_file}...")
        try:
            # Read the file but skip the header row
            df = pd.read_csv(os.path.join(self.data_dir, drivers_file))
            
            # Process Common drivers
            common_end = df[df['Driver'] == 'Rarity'].index[1]
            common_drivers = df.iloc[0:common_end]
            self._process_driver_group(common_drivers, "Common")
            
            # Process Rare drivers
            rare_start = common_end + 2  # Skip the rarity row and the blank row
            rare_end = df[df['Driver'] == 'Rarity'].index[2]
            rare_drivers = df.iloc[rare_start:rare_end]
            self._process_driver_group(rare_drivers, "Rare")
            
            # Process Epic drivers
            epic_start = rare_end + 2
            epic_end = df[df['Driver'] == 'Rarity'].index[3]
            epic_drivers = df.iloc[epic_start:epic_end]
            self._process_driver_group(epic_drivers, "Epic")
            
            # Process Legendary drivers
            legendary_start = epic_end + 2
            legendary_drivers = df.iloc[legendary_start:]
            self._process_driver_group(legendary_drivers, "Legendary")
            
            print(f"Successfully loaded {len(self.drivers)} drivers")
            
        except Exception as e:
            print(f"Error loading driver data: {str(e)}")
    
    def _process_driver_group(self, df, rarity):
        """Process a group of drivers from a specific rarity"""
        # Get the row containing the driver names
        driver_names = df.iloc[0].values
        
        # Get the row containing the levels
        levels = df.iloc[2].values
        
        # Get the stat rows
        overtaking = df.iloc[3].values
        defending = df.iloc[4].values
        qualifying = df.iloc[5].values
        race_start = df.iloc[6].values
        tyre_mgmt = df.iloc[7].values
        total_value = df.iloc[8].values
        series = df.iloc[9].values
        
        # Store each driver's data
        for i in range(1, len(driver_names)):
            if pd.notna(driver_names[i]) and pd.notna(levels[i]) and levels[i] > 0:
                driver_name = driver_names[i]
                driver_level = int(levels[i])
                
                # Calculate total only if all stats are available
                if pd.notna(overtaking[i]) and pd.notna(defending[i]) and pd.notna(qualifying[i]) and \
                   pd.notna(race_start[i]) and pd.notna(tyre_mgmt[i]):
                    
                    driver_data = {
                        "Name": driver_name,
                        "Rarity": rarity,
                        "Level": driver_level,
                        "Overtaking": int(overtaking[i]),
                        "Defending": int(defending[i]),
                        "Qualifying": int(qualifying[i]),
                        "Race_Start": int(race_start[i]),
                        "Tyre_Mgmt": int(tyre_mgmt[i]),
                        "Total_Value": int(total_value[i]),
                        "Series": int(series[i]) if pd.notna(series[i]) else 0
                    }
                    
                    key = f"{driver_name}_{rarity}_{driver_level}"
                    self.drivers[key] = driver_data
                    
                    # Update series limits
                    series_num = int(series[i]) if pd.notna(series[i]) else 0
                    if series_num > 0:
                        if series_num not in self.series_limits:
                            self.series_limits[series_num] = []
                        self.series_limits[series_num].append(key)
    
    def load_components(self, components_file):
        """Parse and organize component data"""
        print(f"Loading components from {components_file}...")
        try:
            df = pd.read_csv(os.path.join(self.data_dir, components_file))
            
            component_types = ["BRAKES", "GEARBOX", "REAR WING", "FRONT WING", "SUSPENSION", "ENGINE"]
            
            for component_type in component_types:
                section_start = df[df.iloc[:, 0] == component_type].index[0]
                if component_type != component_types[-1]:
                    next_type = component_types[component_types.index(component_type) + 1]
                    section_end = df[df.iloc[:, 0] == next_type].index[0]
                else:
                    section_end = len(df)
                
                section_df = df.iloc[section_start:section_end]
                self._process_component_group(section_df, component_type)
            
            print(f"Successfully loaded {len(self.components)} components")
            
        except Exception as e:
            print(f"Error loading component data: {str(e)}")
    
    def _process_component_group(self, df, component_type):
        """Process a group of components of a specific type"""
        # Get component names from the first row (headers)
        component_names = df.iloc[0].values
        
        # Get levels from the "Level" row
        level_row = df[df.iloc[:, 1] == 'Level'].iloc[0]
        levels = level_row.values
        
        # Get stats from respective rows
        speed_row = df[df.iloc[:, 1] == 'Speed'].iloc[0]
        cornering_row = df[df.iloc[:, 1] == 'Cornering'].iloc[0]
        power_unit_row = df[df.iloc[:, 1] == 'Power Unit'].iloc[0]
        qualifying_row = df[df.iloc[:, 1] == 'Qualifying'].iloc[0]
        pit_time_row = df[df.iloc[:, 1] == 'Pit Time'].iloc[0]
        total_value_row = df[df.iloc[:, 1] == 'Total Value'].iloc[0]
        series_row = df[df.iloc[:, 1] == 'Series'].iloc[0]
        
        # Store each component's data (only looking at columns 2-8 which contain the main components)
        for i in range(2, 9):
            if pd.notna(component_names[i]) and pd.notna(levels[i]) and levels[i] > 0:
                component_name = component_names[i]
                component_level = int(levels[i])
                
                # Calculate total only if all stats are available
                if pd.notna(speed_row[i]) and pd.notna(cornering_row[i]) and pd.notna(power_unit_row[i]) and \
                   pd.notna(qualifying_row[i]) and pd.notna(pit_time_row[i]):
                    
                    component_data = {
                        "Name": component_name,
                        "Type": component_type,
                        "Level": component_level,
                        "Speed": float(speed_row[i]),
                        "Cornering": float(cornering_row[i]),
                        "Power_Unit": float(power_unit_row[i]),
                        "Qualifying": float(qualifying_row[i]),
                        "Pit_Time": float(pit_time_row[i]),
                        "Total_Value": float(total_value_row[i]),
                        "Series": float(series_row[i]) if pd.notna(series_row[i]) else 0
                    }
                    
                    key = f"{component_name}_{component_type}_{component_level}"
                    self.components[key] = component_data
                    
                    # Update series limits
                    series_num = int(series_row[i]) if pd.notna(series_row[i]) else 0
                    if series_num > 0:
                        if series_num not in self.series_limits:
                            self.series_limits[series_num] = []
                        self.series_limits[series_num].append(key)
    
    def generate_summary_files(self):
        """Generate summary files for drivers and components"""
        # Save drivers by rarity
        common_drivers = {k: v for k, v in self.drivers.items() if v["Rarity"] == "Common"}
        rare_drivers = {k: v for k, v in self.drivers.items() if v["Rarity"] == "Rare"}
        epic_drivers = {k: v for k, v in self.drivers.items() if v["Rarity"] == "Epic"}
        legendary_drivers = {k: v for k, v in self.drivers.items() if v["Rarity"] == "Legendary"}
        
        # Sort by total value
        sorted_common_drivers = dict(sorted(common_drivers.items(), key=lambda item: item[1]["Total_Value"], reverse=True))
        sorted_rare_drivers = dict(sorted(rare_drivers.items(), key=lambda item: item[1]["Total_Value"], reverse=True))
        sorted_epic_drivers = dict(sorted(epic_drivers.items(), key=lambda item: item[1]["Total_Value"], reverse=True))
        sorted_legendary_drivers = dict(sorted(legendary_drivers.items(), key=lambda item: item[1]["Total_Value"], reverse=True))
        
        # Save component categories
        brakes = {k: v for k, v in self.components.items() if v["Type"] == "BRAKES"}
        gearbox = {k: v for k, v in self.components.items() if v["Type"] == "GEARBOX"}
        rear_wing = {k: v for k, v in self.components.items() if v["Type"] == "REAR WING"}
        front_wing = {k: v for k, v in self.components.items() if v["Type"] == "FRONT WING"}
        suspension = {k: v for k, v in self.components.items() if v["Type"] == "SUSPENSION"}
        engine = {k: v for k, v in self.components.items() if v["Type"] == "ENGINE"}
        
        # Sort by total value
        sorted_brakes = dict(sorted(brakes.items(), key=lambda item: item[1]["Total_Value"], reverse=True))
        sorted_gearbox = dict(sorted(gearbox.items(), key=lambda item: item[1]["Total_Value"], reverse=True))
        sorted_rear_wing = dict(sorted(rear_wing.items(), key=lambda item: item[1]["Total_Value"], reverse=True))
        sorted_front_wing = dict(sorted(front_wing.items(), key=lambda item: item[1]["Total_Value"], reverse=True))
        sorted_suspension = dict(sorted(suspension.items(), key=lambda item: item[1]["Total_Value"], reverse=True))
        sorted_engine = dict(sorted(engine.items(), key=lambda item: item[1]["Total_Value"], reverse=True))
        
        # Write summary CSV files
        self._write_driver_summary("common_drivers.csv", sorted_common_drivers)
        self._write_driver_summary("rare_drivers.csv", sorted_rare_drivers)
        self._write_driver_summary("epic_drivers.csv", sorted_epic_drivers)
        self._write_driver_summary("legendary_drivers.csv", sorted_legendary_drivers)
        
        self._write_component_summary("brakes.csv", sorted_brakes)
        self._write_component_summary("gearbox.csv", sorted_gearbox)
        self._write_component_summary("rear_wing.csv", sorted_rear_wing)
        self._write_component_summary("front_wing.csv", sorted_front_wing)
        self._write_component_summary("suspension.csv", sorted_suspension)
        self._write_component_summary("engine.csv", sorted_engine)
        
        # Save series limits
        with open(os.path.join(self.output_dir, "series_limits.json"), "w") as f:
            json.dump(self.series_limits, f, indent=4)
    
    def _write_driver_summary(self, filename, drivers_dict):
        """Write summary CSV file for a group of drivers"""
        if not drivers_dict:
            return
            
        df = pd.DataFrame([v for v in drivers_dict.values()])
        df = df[["Name", "Rarity", "Level", "Overtaking", "Defending", "Qualifying", 
                "Race_Start", "Tyre_Mgmt", "Total_Value", "Series"]]
        df.to_csv(os.path.join(self.output_dir, filename), index=False)
    
    def _write_component_summary(self, filename, components_dict):
        """Write summary CSV file for a group of components"""
        if not components_dict:
            return
            
        df = pd.DataFrame([v for v in components_dict.values()])
        df = df[["Name", "Type", "Level", "Speed", "Cornering", "Power_Unit", 
                "Qualifying", "Pit_Time", "Total_Value", "Series"]]
        df.to_csv(os.path.join(self.output_dir, filename), index=False)
    
    def find_optimal_drivers(self, series_limit=None, qualifying_target=None, prioritize_stat=None):
        """Find the optimal driver combination based on criteria"""
        valid_drivers = self.drivers.copy()
        
        # Filter by series if needed
        if series_limit is not None:
            valid_drivers = {k: v for k, v in valid_drivers.items() if v["Series"] <= series_limit}
        
        # Sort drivers by total value
        sorted_drivers = sorted(valid_drivers.values(), key=lambda x: x["Total_Value"], reverse=True)
        
        # Find best driver pairs (simple approach - top combinations by total value)
        best_pairs = []
        for i in range(len(sorted_drivers)):
            for j in range(i+1, len(sorted_drivers)):
                driver1 = sorted_drivers[i]
                driver2 = sorted_drivers[j]
                
                combined_value = driver1["Total_Value"] + driver2["Total_Value"]
                combined_qualifying = driver1["Qualifying"] + driver2["Qualifying"]
                
                # Skip if qualifying target is specified and not met
                if qualifying_target and combined_qualifying < qualifying_target:
                    continue
                
                # Calculate priority stat if specified
                priority_value = None
                if prioritize_stat:
                    if prioritize_stat in ["Overtaking", "Defending", "Qualifying", "Race_Start", "Tyre_Mgmt"]:
                        priority_value = driver1[prioritize_stat] + driver2[prioritize_stat]
                
                pair_info = {
                    "Driver1": f"{driver1['Name']} ({driver1['Rarity']}, L{driver1['Level']})",
                    "Driver2": f"{driver2['Name']} ({driver2['Rarity']}, L{driver2['Level']})",
                    "Total_Value": combined_value,
                    "Overtaking": driver1["Overtaking"] + driver2["Overtaking"],
                    "Defending": driver1["Defending"] + driver2["Defending"],
                    "Qualifying": combined_qualifying,
                    "Race_Start": driver1["Race_Start"] + driver2["Race_Start"],
                    "Tyre_Mgmt": driver1["Tyre_Mgmt"] + driver2["Tyre_Mgmt"]
                }
                
                best_pairs.append(pair_info)
        
        # Sort by priority stat if specified, otherwise by total value
        if prioritize_stat and any(p.get(prioritize_stat) for p in best_pairs):
            best_pairs.sort(key=lambda x: x.get(prioritize_stat, 0), reverse=True)
        else:
            best_pairs.sort(key=lambda x: x["Total_Value"], reverse=True)
        
        # Take top 10
        best_pairs = best_pairs[:10]
        
        # Save to CSV
        if best_pairs:
            df = pd.DataFrame(best_pairs)
            output_file = "optimal_drivers.csv"
            if series_limit:
                output_file = f"optimal_drivers_series{series_limit}.csv"
            df.to_csv(os.path.join(self.output_dir, output_file), index=False)
            print(f"Saved optimal driver combinations to {output_file}")
        
        return best_pairs
    
    def find_optimal_components(self, series_limit=None, qualifying_target=None, maximize_speed=False):
        """Find the optimal component setup based on criteria"""
        # Group components by type
        brakes = [v for k, v in self.components.items() if v["Type"] == "BRAKES"]
        gearbox = [v for k, v in self.components.items() if v["Type"] == "GEARBOX"]
        rear_wing = [v for k, v in self.components.items() if v["Type"] == "REAR WING"]
        front_wing = [v for k, v in self.components.items() if v["Type"] == "FRONT WING"]
        suspension = [v for k, v in self.components.items() if v["Type"] == "SUSPENSION"]
        engine = [v for k, v in self.components.items() if v["Type"] == "ENGINE"]
        
        # Filter by series if needed
        if series_limit is not None:
            brakes = [c for c in brakes if c["Series"] <= series_limit]
            gearbox = [c for c in gearbox if c["Series"] <= series_limit]
            rear_wing = [c for c in rear_wing if c["Series"] <= series_limit]
            front_wing = [c for c in front_wing if c["Series"] <= series_limit]
            suspension = [c for c in suspension if c["Series"] <= series_limit]
            engine = [c for c in engine if c["Series"] <= series_limit]
        
        # Sort components by speed if maximizing speed, otherwise by total value
        key_func = lambda x: x["Speed"] if maximize_speed else x["Total_Value"]
        
        brakes.sort(key=key_func, reverse=True)
        gearbox.sort(key=key_func, reverse=True)
        rear_wing.sort(key=key_func, reverse=True)
        front_wing.sort(key=key_func, reverse=True)
        suspension.sort(key=key_func, reverse=True)
        engine.sort(key=key_func, reverse=True)
        
        # Find top combinations that meet qualifying target
        best_setups = []
        
        # This is a simplified approach - in reality would need to check more combinations
        # Just using top components for demonstration
        max_to_check = min(3, min(len(brakes), len(gearbox), len(rear_wing), 
                               len(front_wing), len(suspension), len(engine)))
        
        for b in range(max_to_check):
            for g in range(max_to_check):
                for r in range(max_to_check):
                    for f in range(max_to_check):
                        for s in range(max_to_check):
                            for e in range(max_to_check):
                                if b < len(brakes) and g < len(gearbox) and r < len(rear_wing) and \
                                   f < len(front_wing) and s < len(suspension) and e < len(engine):
                                    
                                    total_qualifying = (brakes[b]["Qualifying"] + gearbox[g]["Qualifying"] + 
                                                      rear_wing[r]["Qualifying"] + front_wing[f]["Qualifying"] + 
                                                      suspension[s]["Qualifying"] + engine[e]["Qualifying"])
                                    
                                    # Skip if qualifying target is specified and not met
                                    if qualifying_target and total_qualifying < qualifying_target:
                                        continue
                                    
                                    total_speed = (brakes[b]["Speed"] + gearbox[g]["Speed"] + 
                                                 rear_wing[r]["Speed"] + front_wing[f]["Speed"] + 
                                                 suspension[s]["Speed"] + engine[e]["Speed"])
                                    
                                    total_value = (brakes[b]["Total_Value"] + gearbox[g]["Total_Value"] + 
                                                 rear_wing[r]["Total_Value"] + front_wing[f]["Total_Value"] + 
                                                 suspension[s]["Total_Value"] + engine[e]["Total_Value"])
                                    
                                    setup_info = {
                                        "Brakes": f"{brakes[b]['Name']} (L{brakes[b]['Level']})",
                                        "Gearbox": f"{gearbox[g]['Name']} (L{gearbox[g]['Level']})",
                                        "Rear_Wing": f"{rear_wing[r]['Name']} (L{rear_wing[r]['Level']})",
                                        "Front_Wing": f"{front_wing[f]['Name']} (L{front_wing[f]['Level']})",
                                        "Suspension": f"{suspension[s]['Name']} (L{suspension[s]['Level']})",
                                        "Engine": f"{engine[e]['Name']} (L{engine[e]['Level']})",
                                        "Total_Value": total_value,
                                        "Total_Speed": total_speed,
                                        "Total_Qualifying": total_qualifying,
                                        "Total_Cornering": (brakes[b]["Cornering"] + gearbox[g]["Cornering"] + 
                                                          rear_wing[r]["Cornering"] + front_wing[f]["Cornering"] + 
                                                          suspension[s]["Cornering"] + engine[e]["Cornering"]),
                                        "Total_Power_Unit": (brakes[b]["Power_Unit"] + gearbox[g]["Power_Unit"] + 
                                                           rear_wing[r]["Power_Unit"] + front_wing[f]["Power_Unit"] + 
                                                           suspension[s]["Power_Unit"] + engine[e]["Power_Unit"])
                                    }
                                    
                                    best_setups.append(setup_info)
        
        # Sort by speed if maximizing speed, otherwise by total value
        sort_key = "Total_Speed" if maximize_speed else "Total_Value"
        best_setups.sort(key=lambda x: x[sort_key], reverse=True)
        
        # Take top 10
        best_setups = best_setups[:10]
        
        # Save to CSV
        if best_setups:
            df = pd.DataFrame(best_setups)
            output_file = "optimal_components.csv"
            if series_limit:
                output_file = f"optimal_components_series{series_limit}.csv"
            if maximize_speed:
                output_file = output_file.replace(".csv", "_speed.csv")
            if qualifying_target:
                output_file = output_file.replace(".csv", f"_qual{qualifying_target}.csv")
            
            df.to_csv(os.path.join(self.output_dir, output_file), index=False)
            print(f"Saved optimal component setups to {output_file}")
        
        return best_setups

# Direct execution
if __name__ == "__main__":
    analyzer = F1ClashAnalyzer()
    
    # Default files
    drivers_file = "F1 Clash 2024 Resourse Sheet 1.7 by TR The Flash - Drivers Horizontal.csv"
    components_file = "F1 Clash 2024 Resourse Sheet 1.7 by TR The Flash - Components Horizontal.csv"
    
    # Check if files exist, otherwise prompt
    data_dir = "data"
    if not os.path.exists(os.path.join(data_dir, drivers_file)):
        print(f"Warning: {drivers_file} not found in {data_dir} directory.")
        drivers_file = input("Enter drivers CSV filename (or press Enter to skip): ")
    
    if not os.path.exists(os.path.join(data_dir, components_file)):
        print(f"Warning: {components_file} not found in {data_dir} directory.")
        components_file = input("Enter components CSV filename (or press Enter to skip): ")
    
    # Load data
    analyzer.load_data(
        drivers_file=drivers_file if drivers_file else None,
        components_file=components_file if components_file else None
    )
    
    # Run some example analyses
    print("\nRunning example analyses...")
    
    # Find optimal drivers
    print("\nFinding optimal driver combinations...")
    analyzer.find_optimal_drivers()
    analyzer.find_optimal_drivers(series_limit=6)
    analyzer.find_optimal_drivers(series_limit=6, prioritize_stat="Overtaking")
    
    # Find optimal components
    print("\nFinding optimal component setups...")
    analyzer.find_optimal_components()
    analyzer.find_optimal_components(series_limit=6)
    analyzer.find_optimal_components(series_limit=6, qualifying_target=110, maximize_speed=True)
    
    print("\nAnalysis complete. Results saved to the output directory.") 