import os
import sys
import shutil
import subprocess
import argparse

def check_requirements():
    """Check if required packages are installed"""
    required_packages = ["pandas", "matplotlib", "seaborn", "numpy", "tabulate"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nPlease install them with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def copy_csv_files():
    """Copy CSV files to the data directory if they're in the current directory"""
    if not os.path.exists("data"):
        os.makedirs("data", exist_ok=True)
    
    # Check for driver and component CSV files in current directory
    for file in os.listdir():
        if "Drivers Horizontal.csv" in file:
            shutil.copy(file, os.path.join("data", file))
            print(f"Copied {file} to data directory")
        elif "Components Horizontal.csv" in file:
            shutil.copy(file, os.path.join("data", file))
            print(f"Copied {file} to data directory")

def run_analysis(series_limit=None, qualifying_target=None, prioritize_speed=False):
    """Run the analysis pipeline"""
    # Run analysis script
    analyze_cmd = [sys.executable, "analyze.py"]
    if series_limit or qualifying_target or prioritize_speed:
        print("Custom analysis requested:")
        if series_limit:
            print(f"  - Series limit: {series_limit}")
        if qualifying_target:
            print(f"  - Qualifying target: {qualifying_target}")
        if prioritize_speed:
            print(f"  - Prioritizing speed")
        
        # We would need to modify the analyze.py script to accept command line arguments
        # For now, we'll just print a message
        print("\nNote: Custom analysis parameters require modifying the analyze.py script directly.")
    
    print("\nRunning data analysis...")
    subprocess.run(analyze_cmd)
    
    # Run visualization script
    print("\nGenerating visualizations and reports...")
    subprocess.run([sys.executable, "visualize.py"])
    
    print("\nAnalysis complete. Results are in the 'output' directory.")

def main():
    """Main entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run F1 Clash analysis pipeline")
    parser.add_argument("--series", type=int, help="Limit analysis to a specific series (e.g., 6)")
    parser.add_argument("--qualifying", type=int, help="Set qualifying target (e.g., 110)")
    parser.add_argument("--speed", action="store_true", help="Prioritize speed in component analysis")
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("F1 Clash Analysis Pipeline")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Copy CSV files if needed
    copy_csv_files()
    
    # Run analysis
    run_analysis(
        series_limit=args.series,
        qualifying_target=args.qualifying,
        prioritize_speed=args.speed
    )
    
    # Print report locations
    if os.path.exists("output"):
        reports = [f for f in os.listdir("output") if f.startswith("report_") or f == "track_recommendations.md"]
        if reports:
            print("\nGenerated reports:")
            for report in reports:
                print(f"  - output/{report}")
    
    print("\nThank you for using the F1 Clash Analysis Tools!")

if __name__ == "__main__":
    main() 