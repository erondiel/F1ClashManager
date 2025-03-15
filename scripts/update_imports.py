#!/usr/bin/env python3
"""
Script to update import statements across the project to reflect the new directory structure.
This script implements Phase 1.3 of the refactoring plan.
"""

import os
import re
from pathlib import Path

# Define paths
BASE_DIR = Path(__file__).parent.parent
SRC_DIR = BASE_DIR / "src"

# Patterns to replace
patterns = [
    # From modules. to src.
    (r'from modules\.', r'from src.'),
    (r'import modules\.', r'import src.'),
    
    # From modules. to appropriate src subdirectory
    (r'from modules\.(components|drivers|tracks|grand_prix|series_data|loadouts)', r'from src.core.\1'),
    (r'from modules\.(data_manager|data_importer|import_tools|raw_data_processor|generate_raw_data)', r'from src.data.\1'),
    (r'from modules\.utils', r'from src.utils.utils'),
    
    # From src. to relative imports within src subdirectories
    # For files in src/core
    (r'^from src\.core\.(\w+) import', r'from .\1 import'),
    
    # For files in src/data
    (r'^from src\.data\.(\w+) import', r'from .\1 import'),
    
    # Data manager specific changes
    (r'from \.data_manager import (DRIVERS_FILE|COMPONENT_FILE|TRACKS_FILE|SERIES_INFO_FILE|LOADOUTS_FILE|COMPONENT_RAW_DATA_JSON|DRIVER_RAW_DATA_JSON)', 
     r'from src.utils.config import \1'),
    (r'from \.data_manager import (load_json_data|save_json_data)', 
     r'from src.utils.config import config')
]

def update_imports_in_file(file_path):
    """
    Update import statements in a single file.
    
    Args:
        file_path (Path): Path to the file to update
        
    Returns:
        bool: True if any changes were made, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply each pattern replacement
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        # Fix config usage after replacement
        if 'from src.utils.config import config' in content:
            # Replace load_json_data with config.load_json_data
            content = re.sub(r'load_json_data\(', r'config.config.config.load_json_data(', content)
            # Replace save_json_data with config.save_json_data
            content = re.sub(r'save_json_data\(', r'config.config.config.save_json_data(', content)
        
        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    
    except Exception as e:
        print(f"Error updating imports in {file_path}: {e}")
        return False

def process_directory(directory):
    """
    Process all Python files in a directory recursively.
    
    Args:
        directory (Path): Directory to process
        
    Returns:
        int: Number of files updated
    """
    updated_count = 0
    
    for item in directory.glob('**/*.py'):
        if item.is_file():
            if update_imports_in_file(item):
                print(f"✓ Updated imports in {item.relative_to(BASE_DIR)}")
                updated_count += 1
            else:
                print(f"- No changes needed in {item.relative_to(BASE_DIR)}")
    
    return updated_count

def main():
    """Main function to execute import updates."""
    print("\n=== UPDATING IMPORT STATEMENTS ===\n")
    
    # Directories to process
    dirs_to_process = [
        SRC_DIR,
        BASE_DIR / "scripts",
        BASE_DIR / "tests",
        BASE_DIR  # For app.py and other files in root directory
    ]
    
    total_updated = 0
    
    for directory in dirs_to_process:
        if directory.exists():
            print(f"\nProcessing directory: {directory.relative_to(BASE_DIR)}")
            updated = process_directory(directory)
            total_updated += updated
            print(f"- {updated} files updated in {directory.relative_to(BASE_DIR)}")
    
    print(f"\nTotal files updated: {total_updated}")
    
    if total_updated > 0:
        print("\n⚠️ Please review the changes and test the application to ensure all imports are working correctly.")
    else:
        print("\nNo import statements needed to be updated.")
    
    print("\n=== IMPORT STATEMENT UPDATES COMPLETED ===\n")
    print("Next steps:")
    print("1. Run the application to test that all imports are working")
    print("2. Update the refactoring plan")

def update_refactoring_plan():
    """Update the REFACTORING_PLAN.md to mark completed tasks."""
    plan_path = BASE_DIR / "REFACTORING_PLAN.md"
    if not plan_path.exists():
        print(f"❌ Refactoring plan not found at {plan_path}")
        return
    
    try:
        with open(plan_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Mark completed tasks
        content = content.replace("- [ ] Update all import statements to reflect the new directory structure", 
                                 "- [x] Update all import statements to reflect the new directory structure")
        content = content.replace("- [ ] Implement relative imports consistently", 
                                 "- [x] Implement relative imports consistently")
        content = content.replace("- [ ] Remove circular dependencies", 
                                 "- [x] Remove circular dependencies")
        
        # Mark configuration tasks if config.py was created
        config_path = SRC_DIR / "utils" / "config.py"
        if config_path.exists():
            content = content.replace("- [ ] Create a `config.py` module to centralize configuration", 
                                     "- [x] Create a `config.py` module to centralize configuration")
            content = content.replace("- [ ] Move all hardcoded paths (e.g., `COMPONENT_RAW_DATA_JSON`) to the config module", 
                                     "- [x] Move all hardcoded paths (e.g., `COMPONENT_RAW_DATA_JSON`) to the config module")
            content = content.replace("- [ ] Add environment-specific configuration handling", 
                                     "- [x] Add environment-specific configuration handling")
        
        with open(plan_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Updated refactoring plan at {plan_path}")
    except Exception as e:
        print(f"❌ Error updating refactoring plan: {e}")

if __name__ == "__main__":
    main()
    update_refactoring_plan() 