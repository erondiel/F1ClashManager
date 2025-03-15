#!/usr/bin/env python3
"""
Configuration module for F1ClashAnalysis.
This module centralizes all configuration settings and paths.
"""

import os
import json
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
RAW_DATA_DIR = DATA_DIR / "raw"
TEMP_DIR = BASE_DIR / "temp_uploads"

# Ensure directories exist
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# Data files (using pathlib for cross-platform compatibility)
DRIVERS_FILE = PROCESSED_DATA_DIR / "drivers.json"
COMPONENT_FILE = PROCESSED_DATA_DIR / "components.json"
TRACKS_FILE = PROCESSED_DATA_DIR / "tracks.json"
SERIES_INFO_FILE = PROCESSED_DATA_DIR / "series.json"
LOADOUTS_FILE = PROCESSED_DATA_DIR / "loadouts.json"
TRACK_BOOSTS_FILE = PROCESSED_DATA_DIR / "track_boosts.json"
BOOSTS_FILE = PROCESSED_DATA_DIR / "boosts.json"
SERIES_SETUPS_FILE = PROCESSED_DATA_DIR / "series_setups.json"

# Raw data files
COMPONENT_RAW_DATA_JSON = RAW_DATA_DIR / "component_raw_data.json"
DRIVER_RAW_DATA_JSON = RAW_DATA_DIR / "driver_raw_data.json"

# Default filenames for temporary uploads
DEFAULT_TRACKER_UPLOAD = TEMP_DIR / "tracker_data.csv"
DEFAULT_COMPONENT_UPLOAD = TEMP_DIR / "component_data.csv"
DEFAULT_DRIVER_UPLOAD = TEMP_DIR / "driver_data.csv"

# Application settings
APP_TITLE = "F1 Clash Manager"
DEFAULT_THEME = "light"

# Versioning
APP_VERSION = "1.0.0"  # Should be updated with each release

class Config:
    """Configuration class for F1ClashAnalysis."""
    
    @staticmethod
    def get_file_path(file_key):
        """
        Get the path for a specific file by key.
        
        Args:
            file_key (str): Key for the file path (e.g., 'drivers', 'components')
            
        Returns:
            Path: Path object for the requested file
        """
        file_map = {
            'drivers': DRIVERS_FILE,
            'components': COMPONENT_FILE,
            'tracks': TRACKS_FILE,
            'series': SERIES_INFO_FILE,
            'loadouts': LOADOUTS_FILE,
            'track_boosts': TRACK_BOOSTS_FILE,
            'boosts': BOOSTS_FILE,
            'series_setups': SERIES_SETUPS_FILE,
            'component_raw': COMPONENT_RAW_DATA_JSON,
            'driver_raw': DRIVER_RAW_DATA_JSON
        }
        
        if file_key not in file_map:
            raise ValueError(f"Invalid file key: {file_key}")
        
        return file_map[file_key]
    
    @staticmethod
    def load_json_data(file_path):
        """
        Load JSON data from a file.
        
        Args:
            file_path (str or Path): Path to the JSON file
            
        Returns:
            dict: JSON data as a dictionary, or empty dict if file doesn't exist
        """
        file_path = Path(file_path)
        if not file_path.exists():
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON from {file_path}: {e}")
            return {}

    @staticmethod
    def save_json_data(file_path, data):
        """
        Save data to a JSON file.
        
        Args:
            file_path (str or Path): Path to the JSON file
            data (dict): Data to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        file_path = Path(file_path)
        os.makedirs(file_path.parent, exist_ok=True)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving JSON to {file_path}: {e}")
            return False

# Environment-specific configuration
def get_env_config():
    """
    Get configuration based on the current environment.
    
    Returns:
        dict: Environment-specific configuration
    """
    env = os.environ.get('ENV', 'development')
    
    config = {
        'development': {
            'debug': True,
            'log_level': 'DEBUG',
            'use_sample_data': True
        },
        'production': {
            'debug': False,
            'log_level': 'INFO',
            'use_sample_data': False
        },
        'testing': {
            'debug': True,
            'log_level': 'DEBUG',
            'use_sample_data': True,
            'testing': True
        }
    }
    
    return config.get(env, config['development'])

# Get active environment configuration
ENV_CONFIG = get_env_config()

# Export global config instance
config = Config() 