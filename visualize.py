import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate
import numpy as np

class F1ClashVisualizer:
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        self.plots_dir = os.path.join(output_dir, "plots")
        os.makedirs(self.plots_dir, exist_ok=True)
        
        # Set plotting style
        sns.set_style("whitegrid")
        plt.rcParams["figure.figsize"] = (12, 8)
    
    def load_driver_data(self):
        """Load all driver data from summary files"""
        drivers = {}
        
        for rarity in ["common", "rare", "epic", "legendary"]:
            file_path = os.path.join(self.output_dir, f"{rarity}_drivers.csv")
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                for _, row in df.iterrows():
                    key = f"{row['Name']}_{rarity.capitalize()}_{int(row['Level'])}"
                    drivers[key] = row.to_dict()
        
        return drivers
    
    def load_component_data(self):
        """Load all component data from summary files"""
        components = {}
        
        for component_type in ["brakes", "gearbox", "rear_wing", "front_wing", "suspension", "engine"]:
            file_path = os.path.join(self.output_dir, f"{component_type.replace('_', '_')}.csv")
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                for _, row in df.iterrows():
                    key = f"{row['Name']}_{row['Type']}_{int(row['Level'])}"
                    components[key] = row.to_dict()
        
        return components
    
    def plot_driver_stats(self, rarity=None, save=True):
        """Plot driver stats by rarity"""
        for r in (["common", "rare", "epic", "legendary"] if rarity is None else [rarity.lower()]):
            file_path = os.path.join(self.output_dir, f"{r}_drivers.csv")
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                
                if len(df) == 0:
                    continue
                
                # Only keep drivers with Level > 0
                df = df[df['Level'] > 0]
                
                if len(df) == 0:
                    continue
                
                # Create a radar chart for each driver's stats
                attributes = ["Overtaking", "Defending", "Qualifying", "Race_Start", "Tyre_Mgmt"]
                
                for _, driver in df.iterrows():
                    plt.figure(figsize=(10, 8))
                    
                    # Number of variables
                    N = len(attributes)
                    
                    # What will be the angle of each axis in the plot
                    angles = [n / float(N) * 2 * np.pi for n in range(N)]
                    angles += angles[:1]  # Close the loop
                    
                    # Spider plot
                    ax = plt.subplot(111, polar=True)
                    
                    # Add driver stats
                    stats = [driver[attr] for attr in attributes]
                    stats += stats[:1]  # Close the loop
                    
                    # Plot data
                    ax.plot(angles, stats, linewidth=2, linestyle='solid', label=driver['Name'])
                    ax.fill(angles, stats, alpha=0.1)
                    
                    # Set labels
                    plt.xticks(angles[:-1], attributes)
                    
                    # Add title
                    plt.title(f"{driver['Name']} ({r.capitalize()}, Level {int(driver['Level'])})", 
                              size=15, y=1.1)
                    
                    if save:
                        plt.savefig(os.path.join(self.plots_dir, f"driver_{driver['Name']}_{r}_{int(driver['Level'])}.png"))
                        plt.close()
                    else:
                        plt.show()
    
    def plot_component_stats(self, component_type=None, save=True):
        """Plot component stats by type"""
        for c_type in (["brakes", "gearbox", "rear_wing", "front_wing", "suspension", "engine"] 
                       if component_type is None else [component_type.lower().replace(" ", "_")]):
            
            file_path = os.path.join(self.output_dir, f"{c_type}.csv")
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                
                if len(df) == 0:
                    continue
                
                # Only keep components with Level > 0
                df = df[df['Level'] > 0]
                
                if len(df) == 0:
                    continue
                
                # Create a radar chart for each component's stats
                attributes = ["Speed", "Cornering", "Power_Unit", "Qualifying", "Pit_Time"]
                
                for _, component in df.iterrows():
                    plt.figure(figsize=(10, 8))
                    
                    # Number of variables
                    N = len(attributes)
                    
                    # What will be the angle of each axis in the plot
                    angles = [n / float(N) * 2 * np.pi for n in range(N)]
                    angles += angles[:1]  # Close the loop
                    
                    # Spider plot
                    ax = plt.subplot(111, polar=True)
                    
                    # Add component stats
                    stats = [component[attr] for attr in attributes]
                    stats += stats[:1]  # Close the loop
                    
                    # Plot data
                    ax.plot(angles, stats, linewidth=2, linestyle='solid', label=component['Name'])
                    ax.fill(angles, stats, alpha=0.1)
                    
                    # Set labels
                    plt.xticks(angles[:-1], attributes)
                    
                    # Add title
                    plt.title(f"{component['Name']} ({c_type.replace('_', ' ').title()}, Level {int(component['Level'])})", 
                              size=15, y=1.1)
                    
                    if save:
                        plt.savefig(os.path.join(self.plots_dir, 
                                               f"component_{component['Name']}_{c_type}_{int(component['Level'])}.png"))
                        plt.close()
                    else:
                        plt.show()
    
    def create_optimal_setup_reports(self):
        """Create detailed reports for optimal setups"""
        # Check for optimal driver files
        for f in os.listdir(self.output_dir):
            if f.startswith("optimal_drivers") and f.endswith(".csv"):
                self._create_driver_report(f)
                
        # Check for optimal component files
        for f in os.listdir(self.output_dir):
            if f.startswith("optimal_components") and f.endswith(".csv"):
                self._create_component_report(f)
    
    def _create_driver_report(self, filename):
        """Create a detailed report for optimal driver combinations"""
        file_path = os.path.join(self.output_dir, filename)
        df = pd.read_csv(file_path)
        
        if len(df) == 0:
            return
        
        report_lines = []
        report_lines.append(f"# Optimal Driver Combinations - {filename[:-4]}")
        report_lines.append("")
        
        # Find what type of optimization this is
        report_type = "Overall Best"
        if "series" in filename:
            series_num = filename.split("series")[1].split(".")[0]
            report_type = f"Best for Series {series_num}"
            
        report_lines.append(f"## {report_type} Driver Combinations")
        report_lines.append("")
        
        # Add table of top combinations
        headers = df.columns.tolist()
        table_data = df.values.tolist()
        report_lines.append(tabulate(table_data, headers=headers, tablefmt="pipe"))
        report_lines.append("")
        
        # Add detailed analysis of best combination
        best_combo = df.iloc[0]
        report_lines.append(f"## Detailed Analysis of Top Combination")
        report_lines.append("")
        report_lines.append(f"### {best_combo['Driver1']} + {best_combo['Driver2']}")
        report_lines.append("")
        report_lines.append(f"* **Total Value:** {best_combo['Total_Value']}")
        report_lines.append(f"* **Overtaking:** {best_combo['Overtaking']}")
        report_lines.append(f"* **Defending:** {best_combo['Defending']}")
        report_lines.append(f"* **Qualifying:** {best_combo['Qualifying']}")
        report_lines.append(f"* **Race Start:** {best_combo['Race_Start']}")
        report_lines.append(f"* **Tyre Management:** {best_combo['Tyre_Mgmt']}")
        report_lines.append("")
        
        # Add track recommendations based on stats
        report_lines.append("## Track Recommendations")
        report_lines.append("")
        
        # Simple logic for track recommendations
        if best_combo['Overtaking'] > best_combo['Defending']:
            report_lines.append("* **Good for overtaking tracks:** Monza, Spa, Baku")
        else:
            report_lines.append("* **Good for defensive tracks:** Monaco, Singapore, Hungary")
            
        if best_combo['Qualifying'] > best_combo['Race_Start']:
            report_lines.append("* **Strong in qualifying:** Focus on qualifying performance")
        else:
            report_lines.append("* **Strong in race starts:** Can recover from lower grid positions")
            
        if best_combo['Tyre_Mgmt'] > (best_combo['Overtaking'] + best_combo['Defending'])/2:
            report_lines.append("* **Good tyre management:** Consider longer stints and fewer stops")
        
        # Write report to file
        report_path = os.path.join(self.output_dir, f"report_{filename[:-4]}.md")
        with open(report_path, "w") as f:
            f.write("\n".join(report_lines))
            
        print(f"Driver report saved to {report_path}")
    
    def _create_component_report(self, filename):
        """Create a detailed report for optimal component setups"""
        file_path = os.path.join(self.output_dir, filename)
        df = pd.read_csv(file_path)
        
        if len(df) == 0:
            return
        
        report_lines = []
        report_lines.append(f"# Optimal Component Setups - {filename[:-4]}")
        report_lines.append("")
        
        # Find what type of optimization this is
        report_type = "Overall Best"
        if "series" in filename:
            series_num = filename.split("series")[1].split("_")[0]
            report_type = f"Best for Series {series_num}"
        
        if "speed" in filename:
            report_type += " (Speed Optimized)"
            
        if "qual" in filename:
            qual_target = filename.split("qual")[1].split(".")[0]
            report_type += f" (Qualifying Target: {qual_target})"
            
        report_lines.append(f"## {report_type} Component Setup")
        report_lines.append("")
        
        # Add table of best setup
        best_setup = df.iloc[0].to_dict()
        
        setup_table = [
            ["Component Type", "Selected Component", "Total Value", "Speed", "Cornering", "Power Unit", "Qualifying"]
        ]
        
        # Add setup components to the table
        for component_type in ["Brakes", "Gearbox", "Rear_Wing", "Front_Wing", "Suspension", "Engine"]:
            setup_table.append([
                component_type.replace("_", " "),
                best_setup[component_type],
                "", "", "", "", ""  # Would need individual component stats which we don't have here
            ])
        
        # Add totals row
        setup_table.append([
            "TOTALS", 
            "", 
            best_setup["Total_Value"],
            best_setup["Total_Speed"],
            best_setup["Total_Cornering"],
            best_setup["Total_Power_Unit"],
            best_setup["Total_Qualifying"]
        ])
        
        report_lines.append(tabulate(setup_table, headers="firstrow", tablefmt="pipe"))
        report_lines.append("")
        
        # Add track recommendations based on stats
        report_lines.append("## Track Recommendations")
        report_lines.append("")
        
        # Simple logic for track recommendations
        if best_setup['Total_Speed'] > best_setup['Total_Cornering'] and best_setup['Total_Speed'] > best_setup['Total_Power_Unit']:
            report_lines.append("* **Good for high-speed tracks:** Monza, Spa, Baku")
        elif best_setup['Total_Cornering'] > best_setup['Total_Speed'] and best_setup['Total_Cornering'] > best_setup['Total_Power_Unit']:
            report_lines.append("* **Good for technical tracks:** Monaco, Singapore, Hungary")
        else:
            report_lines.append("* **Good for power tracks:** Silverstone, Spa, Austria")
            
        # Add comparison to other setups
        report_lines.append("")
        report_lines.append("## Comparison with Alternative Setups")
        report_lines.append("")
        
        if len(df) > 1:
            comparison_data = []
            for i in range(min(5, len(df))):
                row = df.iloc[i]
                comparison_data.append([
                    f"Setup {i+1}",
                    row["Total_Value"],
                    row["Total_Speed"],
                    row["Total_Cornering"],
                    row["Total_Power_Unit"],
                    row["Total_Qualifying"]
                ])
            
            report_lines.append(tabulate(comparison_data, 
                                        headers=["Setup", "Total Value", "Speed", "Cornering", "Power Unit", "Qualifying"],
                                        tablefmt="pipe"))
        else:
            report_lines.append("No alternative setups to compare.")
        
        # Write report to file
        report_path = os.path.join(self.output_dir, f"report_{filename[:-4]}.md")
        with open(report_path, "w") as f:
            f.write("\n".join(report_lines))
            
        print(f"Component report saved to {report_path}")
    
    def create_track_specific_recommendations(self):
        """Create track-specific recommendations based on available data"""
        tracks = [
            {"name": "Monza", "focus": "Speed", "description": "High-speed track with long straights"},
            {"name": "Monaco", "focus": "Cornering", "description": "Technical street circuit with tight corners"},
            {"name": "Spa", "focus": "Mixed", "description": "Fast track with technical sections"},
            {"name": "Silverstone", "focus": "Power", "description": "Power-hungry circuit with fast corners"},
            {"name": "Singapore", "focus": "Technical", "description": "Street circuit requiring precision"},
            {"name": "Baku", "focus": "Mixed", "description": "Street circuit with long straight and technical sections"}
        ]
        
        # Load optimal component and driver data
        optimal_components_file = None
        optimal_drivers_file = None
        
        for f in os.listdir(self.output_dir):
            if f.startswith("optimal_components") and f.endswith(".csv"):
                optimal_components_file = f
            if f.startswith("optimal_drivers") and f.endswith(".csv"):
                optimal_drivers_file = f
        
        if not optimal_components_file or not optimal_drivers_file:
            print("Missing optimal setup files. Run the analyzer first.")
            return
        
        components_df = pd.read_csv(os.path.join(self.output_dir, optimal_components_file))
        drivers_df = pd.read_csv(os.path.join(self.output_dir, optimal_drivers_file))
        
        # Create track recommendations
        report_lines = []
        report_lines.append("# Track-Specific Setup Recommendations")
        report_lines.append("")
        
        for track in tracks:
            report_lines.append(f"## {track['name']} - {track['description']}")
            report_lines.append("")
            
            # Select appropriate setup based on track focus
            if track['focus'] in ["Speed", "Mixed"]:
                # Use speed-focused setup if available
                speed_components = components_df.sort_values("Total_Speed", ascending=False).iloc[0]
                report_lines.append("### Recommended Components")
                report_lines.append("")
                report_lines.append(f"* **Brakes:** {speed_components['Brakes']}")
                report_lines.append(f"* **Gearbox:** {speed_components['Gearbox']}")
                report_lines.append(f"* **Rear Wing:** {speed_components['Rear_Wing']}")
                report_lines.append(f"* **Front Wing:** {speed_components['Front_Wing']}")
                report_lines.append(f"* **Suspension:** {speed_components['Suspension']}")
                report_lines.append(f"* **Engine:** {speed_components['Engine']}")
                report_lines.append("")
                
                # Select drivers with good overtaking for speed tracks
                overtaking_drivers = drivers_df.sort_values("Overtaking", ascending=False).iloc[0]
                report_lines.append("### Recommended Drivers")
                report_lines.append("")
                report_lines.append(f"* {overtaking_drivers['Driver1']}")
                report_lines.append(f"* {overtaking_drivers['Driver2']}")
                report_lines.append("")
                
            elif track['focus'] in ["Cornering", "Technical"]:
                # Use cornering-focused setup
                cornering_components = components_df.sort_values("Total_Cornering", ascending=False).iloc[0]
                report_lines.append("### Recommended Components")
                report_lines.append("")
                report_lines.append(f"* **Brakes:** {cornering_components['Brakes']}")
                report_lines.append(f"* **Gearbox:** {cornering_components['Gearbox']}")
                report_lines.append(f"* **Rear Wing:** {cornering_components['Rear_Wing']}")
                report_lines.append(f"* **Front Wing:** {cornering_components['Front_Wing']}")
                report_lines.append(f"* **Suspension:** {cornering_components['Suspension']}")
                report_lines.append(f"* **Engine:** {cornering_components['Engine']}")
                report_lines.append("")
                
                # Select drivers with good defending for technical tracks
                defending_drivers = drivers_df.sort_values("Defending", ascending=False).iloc[0]
                report_lines.append("### Recommended Drivers")
                report_lines.append("")
                report_lines.append(f"* {defending_drivers['Driver1']}")
                report_lines.append(f"* {defending_drivers['Driver2']}")
                report_lines.append("")
                
            elif track['focus'] == "Power":
                # Use power-focused setup
                power_components = components_df.sort_values("Total_Power_Unit", ascending=False).iloc[0]
                report_lines.append("### Recommended Components")
                report_lines.append("")
                report_lines.append(f"* **Brakes:** {power_components['Brakes']}")
                report_lines.append(f"* **Gearbox:** {power_components['Gearbox']}")
                report_lines.append(f"* **Rear Wing:** {power_components['Rear_Wing']}")
                report_lines.append(f"* **Front Wing:** {power_components['Front_Wing']}")
                report_lines.append(f"* **Suspension:** {power_components['Suspension']}")
                report_lines.append(f"* **Engine:** {power_components['Engine']}")
                report_lines.append("")
                
                # Select drivers with good qualifying for power tracks
                qualifying_drivers = drivers_df.sort_values("Qualifying", ascending=False).iloc[0]
                report_lines.append("### Recommended Drivers")
                report_lines.append("")
                report_lines.append(f"* {qualifying_drivers['Driver1']}")
                report_lines.append(f"* {qualifying_drivers['Driver2']}")
                report_lines.append("")
            
            # Add race strategy tips
            report_lines.append("### Race Strategy")
            report_lines.append("")
            
            if track['focus'] == "Speed":
                report_lines.append("* Focus on maximizing straight-line speed")
                report_lines.append("* Use DRS zones effectively for overtaking")
                report_lines.append("* Consider low-downforce setup for better top speed")
            elif track['focus'] in ["Cornering", "Technical"]:
                report_lines.append("* Focus on car control and precision")
                report_lines.append("* Qualifying position is crucial - prioritize single-lap pace")
                report_lines.append("* Consider track position over raw pace")
            elif track['focus'] == "Mixed":
                report_lines.append("* Balance speed and cornering performance")
                report_lines.append("* Be strategic about where to overtake")
                report_lines.append("* Consider a balanced downforce setup")
            elif track['focus'] == "Power":
                report_lines.append("* Focus on power unit performance out of corners")
                report_lines.append("* Manage ERS deployment strategically")
                report_lines.append("* Consider medium-high downforce for better cornering speed")
            
            report_lines.append("")
        
        # Write report to file
        report_path = os.path.join(self.output_dir, "track_recommendations.md")
        with open(report_path, "w") as f:
            f.write("\n".join(report_lines))
            
        print(f"Track recommendations saved to {report_path}")

# Direct execution
if __name__ == "__main__":
    visualizer = F1ClashVisualizer()
    
    # Check if output files exist
    if not any(f.endswith('.csv') for f in os.listdir(visualizer.output_dir)):
        print("No data files found. Run analyze.py first to generate data.")
    else:
        # Generate visualizations
        visualizer.plot_driver_stats()
        visualizer.plot_component_stats()
        
        # Create reports
        visualizer.create_optimal_setup_reports()
        visualizer.create_track_specific_recommendations()
        
        print("Visualization and report generation complete.") 