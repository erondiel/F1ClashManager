import json
from src.utils import update_item_upgrade_info

def test_highest_level_calculation():
    """
    Test the highest level calculation function with various sample data.
    This verifies that the logic matches the spreadsheet formula:
    =if(C2=0;0;if($I2<$K$4;1;if($I2<$K$5;2;if($I2<$K$6;3;if($I2<$K$7;4;if($I2<$K$8;5;if($I2<$K$9;6;if($I2<$K$10;7;if($I2<$K$11;8;if($I2<$K$12;9;if($I2<$K$13;10;11)))))))))))
    
    The test cases are derived from the CSV file examples.
    """
    print("Testing highest level calculation function...")
    print("-" * 80)
    
    # Test cases based on different rarities and card counts
    test_cases = [
        # Test Common drivers - Max cards: 7784
        # Test case from CSV: Colapinto, Common, Level 8, Cards: 1009
        {
            "name": "Colapinto",
            "rarity": "Common",
            "level": 8,
            "cards_owned": 1009,
            "expected_highest": 9,  # Verify this matches the CSV data
            "expected_total": 1793  # 1009 + 784
        },
        # Test case from CSV: Magnussen, Common, Level 7, Cards: 1631
        {
            "name": "Magnussen",
            "rarity": "Common",
            "level": 7,
            "cards_owned": 1631,
            "expected_highest": 9,  # Verify this matches the CSV data
            "expected_total": 2015  # 1631 + 384
        },
        
        # Test Rare components - Max cards: 1784
        # Test case from CSV: Bottas, Rare, Level 7, Cards: 677
        {
            "name": "Bottas",
            "rarity": "Rare", 
            "level": 7,
            "cards_owned": 677,
            "expected_highest": 8,  # Verify this matches the CSV data
            "expected_total": 1061  # 677 + 384
        },
        
        # Test Epic components - Max cards: 784
        # Test case from CSV: Hulkenberg, Epic, Level 6, Cards: 7
        {
            "name": "Hulkenberg",
            "rarity": "Epic",
            "level": 6, 
            "cards_owned": 7,
            "expected_highest": 6,  # Verify this matches the CSV data
            "expected_total": 191   # 7 + 184
        },
        
        # Test zero level
        {
            "name": "Test Zero",
            "rarity": "Common",
            "level": 0,
            "cards_owned": 500,
            "expected_highest": 0,  # Should be 0 if level is 0
            "expected_total": 500   # Just the cards owned
        },
        
        # Test edge cases
        {
            "name": "Almost Level 9",
            "rarity": "Common",
            "level": 8,
            "cards_owned": 783,  # 1 less than threshold for level 9
            "expected_highest": 8,
            "expected_total": 1567  # 783 + 784
        },
        {
            "name": "Exactly Level 9",
            "rarity": "Common",
            "level": 8,
            "cards_owned": 784,  # Exactly at threshold
            "expected_highest": 9,
            "expected_total": 1568  # 784 + 784
        }
    ]
    
    # Run each test case
    for i, test in enumerate(test_cases):
        print(f"Test Case {i+1}: {test['name']} ({test['rarity']}, Level {test['level']})")
        
        # Create a sample item
        item = {
            "name": test["name"],
            "rarity": test["rarity"],
            "level": test["level"],
            "inInventory": test["level"] > 0,
            "upgradeInfo": {}  # This will be populated by the function
        }
        
        # Apply the calculation
        updated_item = update_item_upgrade_info(item, test["cards_owned"])
        
        # Get results
        highest_level = updated_item["highestLevel"]
        total_cards = updated_item["upgradeInfo"]["totalCards"]
        
        # Check if results match expectations
        highest_level_correct = highest_level == test["expected_highest"]
        total_cards_correct = total_cards == test["expected_total"]
        
        # Print results
        print(f"  Cards Owned: {test['cards_owned']}")
        print(f"  Cards Per Level: {updated_item['upgradeInfo']['perLevel']}")
        print(f"  Total Cards: {total_cards} (Expected: {test['expected_total']}) - {'✓' if total_cards_correct else '✗'}")
        print(f"  Highest Level: {highest_level} (Expected: {test['expected_highest']}) - {'✓' if highest_level_correct else '✗'}")
        print(f"  Max Cards: {updated_item['upgradeInfo']['maxCards']}")
        print(f"  Cards Needed: {updated_item['upgradeInfo']['cardsNeeded']}")
        
        if not (highest_level_correct and total_cards_correct):
            print("  ⚠️ Test failed!")
        else:
            print("  ✅ Test passed!")
        
        print()
    
    print("-" * 80)
    print("Test completed. Check for any failures above.")

if __name__ == "__main__":
    test_highest_level_calculation() 