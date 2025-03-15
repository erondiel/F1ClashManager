import pandas as pd
import re
import datetime

def clean_numeric(value):
    """Remove commas from numeric strings and convert to int or float."""
    if isinstance(value, str):
        return value.replace(',', '')
    return value
    
def safe_int(value):
    """Safely convert a value to int, handling commas and returning 0 if invalid."""
    if pd.isna(value):
        return 0
    try:
        # First remove any commas
        if isinstance(value, str):
            value = value.replace(',', '')
        return int(float(value))
    except (ValueError, TypeError):
        return 0
        
def safe_float(value):
    """Safely convert a value to float, handling commas and returning 0.0 if invalid."""
    if pd.isna(value):
        return 0.0
    try:
        # First remove any commas
        if isinstance(value, str):
            value = value.replace(',', '')
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def format_number(value, decimal_places=1):
    """Format a number to a specified number of decimal places and remove trailing zeros."""
    formatted = f"{float(value):.{decimal_places}f}"
    if '.' in formatted:
        return formatted.rstrip('0').rstrip('.')
    return formatted

def get_current_timestamp():
    """Get the current timestamp in the format used for loadouts."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 

def calculate_highest_level(item, cards_owned):
    """
    Calculate the highest level an item can be upgraded to based on cards owned.
    
    Args:
        item (dict): The item dictionary containing level and rarity information
        cards_owned (int): The number of cards owned for this item
        
    Returns:
        int: The highest possible level
    """
    # If level is 0, the item is not in inventory
    if item["level"] == 0:
        return 0
    
    # Calculate cards required per level based on rarity
    cards_per_level = get_cards_per_level(item["rarity"])
    
    # Calculate the maximum level based on cards owned
    current_level = item["level"]
    highest_level = current_level
    
    # Cards required for each level (starting from current level + 1)
    for level in range(current_level + 1, 12):
        cards_needed = cards_per_level.get(level, 0)
        if cards_owned >= cards_needed:
            highest_level = level
            cards_owned -= cards_needed
        else:
            break
    
    return highest_level

def get_cards_per_level(rarity):
    """
    Get the cards required for each level based on rarity.
    
    Args:
        rarity (str): The rarity of the item (Common, Rare, Epic, Legendary)
        
    Returns:
        dict: A dictionary of level -> cards required
    """
    # Cards required to upgrade to each level
    if rarity == "Common":
        return {
            2: 4,
            3: 10,
            4: 20,
            5: 50,
            6: 100,
            7: 200,
            8: 400,
            9: 800,
            10: 1000,
            11: 5000
        }
    elif rarity == "Rare":
        return {
            2: 2,
            3: 5,
            4: 10,
            5: 20,
            6: 50,
            7: 100,
            8: 200,
            9: 400,
            10: 500,
            11: 2000
        }
    elif rarity == "Epic":
        return {
            2: 1,
            3: 2,
            4: 5,
            5: 10,
            6: 20,
            7: 50,
            8: 100,
            9: 200,
            10: 250,
            11: 800
        }
    elif rarity == "Legendary":
        return {
            2: 1,
            3: 1,
            4: 2,
            5: 5,
            6: 10,
            7: 20,
            8: 50,
            9: 100,
            10: 150,
            11: 400
        }
    else:
        return {}

def update_item_upgrade_info(item, cards_owned):
    """
    Update an item with upgrade information based on cards owned.
    
    Args:
        item (dict): The item dictionary to update
        cards_owned (int): The number of cards owned for this item
        
    Returns:
        dict: The updated item dictionary
    """
    # Get cards per level based on rarity
    cards_per_level = get_cards_per_level(item["rarity"])
    
    # Calculate the maximum number of cards needed for the rarity
    max_cards = sum(cards_per_level.values())
    
    # Calculate the highest possible level
    highest_level = calculate_highest_level(item, cards_owned)
    
    # Calculate the total number of cards (owned + already used for upgrades)
    used_cards = sum([cards_per_level.get(level, 0) for level in range(2, item["level"] + 1)])
    total_cards = cards_owned + used_cards
    
    # Calculate cards needed to reach the maximum level
    remaining_levels = [level for level in range(item["level"] + 1, 12)]
    cards_needed = sum([cards_per_level.get(level, 0) for level in remaining_levels])
    
    # Update the item dictionary
    item["highestLevel"] = highest_level
    item["upgradeInfo"] = {
        "cardsOwned": cards_owned,
        "perLevel": cards_per_level,
        "maxCards": max_cards,
        "cardsNeeded": cards_needed,
        "totalCards": total_cards
    }
    
    return item 