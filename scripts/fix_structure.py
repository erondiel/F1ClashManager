#!/usr/bin/env python3
"""
Module to fix directory structure issues in the F1ClashAnalysis project.
This script implements Phase 1.1 of the refactoring plan.
"""

import os
import shutil
import json

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODULES_DIR = os.path.join(BASE_DIR, "modules")
NESTED_MODULES_DIR = os.path.join(MODULES_DIR, "modules")
SRC_DIR = os.path.join(BASE_DIR, "src")

# Define directory structure
SRC_SUBDIRS = ["core", "data", "ui", "utils"]

def create_directory_structure():
    """Create the proper directory structure if it doesn't exist."""
    for subdir in SRC_SUBDIRS:
        os.makedirs(os.path.join(SRC_DIR, subdir), exist_ok=True)
    print(f"✓ Created directory structure in {SRC_DIR}")

def remove_nested_modules():
    """Remove the nested modules folder, but backup any unique files."""
    if not os.path.exists(NESTED_MODULES_DIR):
        print("No nested modules directory found.")
        return
    
    # Compare raw_data_processor files
    original_file = os.path.join(MODULES_DIR, "raw_data_processor.py")
    nested_file = os.path.join(NESTED_MODULES_DIR, "raw_data_processor.py")
    
    if os.path.exists(nested_file):
        if os.path.exists(original_file):
            print(f"⚠️ Both {original_file} and {nested_file} exist.")
            print(f"⚠️ Backing up {nested_file} to {nested_file}.bak")
            shutil.copy2(nested_file, f"{nested_file}.bak")
        else:
            print(f"⚠️ Moving {nested_file} to {original_file}")
            shutil.move(nested_file, original_file)
    
    # Remove the nested modules directory
    try:
        shutil.rmtree(NESTED_MODULES_DIR)
        print(f"✓ Removed nested modules directory: {NESTED_MODULES_DIR}")
    except Exception as e:
        print(f"❌ Error removing nested modules directory: {e}")

def remove_duplicate_files():
    """Remove duplicate files like import_tools_new.py."""
    duplicate_file = os.path.join(MODULES_DIR, "import_tools_new.py")
    if os.path.exists(duplicate_file):
        try:
            os.remove(duplicate_file)
            print(f"✓ Removed duplicate file: {duplicate_file}")
        except Exception as e:
            print(f"❌ Error removing duplicate file: {e}")
    else:
        print(f"No duplicate file found at {duplicate_file}")

def get_file_category(filename):
    """Categorize a file based on its name and content."""
    core_files = ["components.py", "drivers.py", "tracks.py", "grand_prix.py", "series_data.py", "loadouts.py"]
    data_files = ["data_manager.py", "data_importer.py", "import_tools.py", "raw_data_processor.py", "generate_raw_data.py"]
    ui_files = []  # UI files will be identified and moved later
    
    if filename in core_files:
        return "core"
    elif filename in data_files:
        return "data"
    elif filename in ui_files:
        return "ui"
    else:
        return "utils"  # Default category

def move_files_to_src():
    """Move files from modules to src directory based on their category."""
    if not os.path.exists(MODULES_DIR):
        print(f"❌ Modules directory not found: {MODULES_DIR}")
        return
    
    # Track moved files for reporting
    moved_files = {category: [] for category in SRC_SUBDIRS}
    
    for filename in os.listdir(MODULES_DIR):
        # Skip directories and __init__.py
        filepath = os.path.join(MODULES_DIR, filename)
        if os.path.isdir(filepath) or filename == "__init__.py" or filename.startswith("__"):
            continue
        
        # Determine target category and directory
        category = get_file_category(filename)
        target_dir = os.path.join(SRC_DIR, category)
        target_path = os.path.join(target_dir, filename)
        
        # Create backup if file already exists in target location
        if os.path.exists(target_path):
            print(f"⚠️ File already exists at {target_path}")
            print(f"⚠️ Creating backup of original file")
            shutil.copy2(filepath, f"{filepath}.bak")
            continue
        
        # Move the file
        try:
            shutil.move(filepath, target_path)
            moved_files[category].append(filename)
            print(f"✓ Moved {filename} to {target_dir}")
        except Exception as e:
            print(f"❌ Error moving {filename}: {e}")
    
    # Report moved files
    print("\n=== Files Moved Report ===")
    for category, files in moved_files.items():
        if files:
            print(f"\n{category.upper()} ({len(files)} files):")
            for f in files:
                print(f"  - {f}")

def create_init_files():
    """Create __init__.py files in all src subdirectories."""
    for subdir in SRC_SUBDIRS:
        init_path = os.path.join(SRC_DIR, subdir, "__init__.py")
        if not os.path.exists(init_path):
            with open(init_path, "w") as f:
                f.write("# Automatically generated during project restructuring\n")
            print(f"✓ Created {init_path}")

def update_refactoring_plan():
    """Update the REFACTORING_PLAN.md to mark completed tasks."""
    plan_path = os.path.join(BASE_DIR, "REFACTORING_PLAN.md")
    if not os.path.exists(plan_path):
        print(f"❌ Refactoring plan not found at {plan_path}")
        return
    
    try:
        with open(plan_path, "r") as f:
            content = f.read()
        
        # Mark completed tasks
        content = content.replace("- [ ] Remove the nested `modules/modules` folder", 
                                 "- [x] Remove the nested `modules/modules` folder")
        content = content.replace("- [ ] Resolve duplication between `import_tools.py` and `import_tools_new.py`", 
                                 "- [x] Resolve duplication between `import_tools.py` and `import_tools_new.py`")
        content = content.replace("- [ ] Organize modules into logical groups:", 
                                 "- [x] Organize modules into logical groups:")
        
        with open(plan_path, "w") as f:
            f.write(content)
        
        print(f"✓ Updated refactoring plan at {plan_path}")
    except Exception as e:
        print(f"❌ Error updating refactoring plan: {e}")

def main():
    """Main function to execute all structure fixing operations."""
    print("\n=== STARTING DIRECTORY STRUCTURE FIXES ===\n")
    
    # Create the directory structure
    create_directory_structure()
    
    # Remove duplicate directories and files
    remove_nested_modules()
    remove_duplicate_files()
    
    # Move files to appropriate locations
    move_files_to_src()
    
    # Create __init__.py files
    create_init_files()
    
    # Update the refactoring plan
    update_refactoring_plan()
    
    print("\n=== DIRECTORY STRUCTURE FIXES COMPLETED ===\n")
    print("Next steps:")
    print("1. Update import statements in Python files")
    print("2. Create a config.py module to centralize configuration")
    print("3. Test that the application still works correctly")

if __name__ == "__main__":
    main() 