import requests
from bs4 import BeautifulSoup
import json
import re
import os

def scrape_mala_kar():
    url = "https://wiki.ironco.re/index.php?title=Mala%27kar"
    try:
        print("Fetching URL...")
        response = requests.get(url)
        response.raise_for_status()
        print(f"Successfully fetched page (status: {response.status_code})")
    except requests.RequestException as e:
        print(f"Error fetching page: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Define categories based on your HTML structure (predefined items stay in their tabs)
    categories = {
        "equipment-mana-gems": [
            "Beholder Shield", "Blue Robe", "Boots of Haste", "Bright Sword", "Crown Armor",
            "Crown Helmet", "Crown Legs", "Crown Shield", "Dark Boots", "Dark Legs",
            "Devil Helmet", "Dragon Hammer", "Dwarven Axe", "Dwarven Shield", "Guardian Shield",
            "Knight Armor", "Knight Axe", "Knight Legs", "Mystic Turban", "Noble Armor",
            "Paladin Armor", "Platinum Amulet", "Red Robe", "Red Tunic", "Silver Mace",
            "Spike Sword", "Strange Helmet", "Warrior Helmet"
        ],
        "items-mana-gems": ["Beads", "Holy Scroll", "Small Oil Lamp"],
        "gear-demonic-mana-gems": ["Dragon Shield", "Steel Boots"],
        "demonic-mana-gems": ["Oil Lamp", "Stone Skin Amulet", "Wedding Ring"]
    }
    
    # Initialize data structure
    data = {
        "equipment-mana-gems": [],
        "items-mana-gems": [],
        "gear-demonic-mana-gems": [],
        "demonic-mana-gems": []
    }

    # Equipment keywords for missing items
    equipment_keywords = ["Armor", "Shield", "Helmet", "Legs", "Boots", "Sword", "Axe", "Mace", "Turban", "Amulet", "Necklace", "Ring", "Hammer", "Robe", "Dagger"]

    # Collect all scraped items first (to avoid duplicates)
    scraped_items = {}
    tables = soup.find_all('table')
    print(f"Found {len(tables)} tables on the page.")

    for i, table in enumerate(tables):
        table_text = table.get_text().lower()
        print(f"Processing table {i+1}...")
        
        # Better currency detection based on table content
        if "demonic" in table_text:
            currency = "Demonic Mana Gems"
        elif "green" in table_text:
            currency = "Mana Gems"  # Treat Green as Mana for your tabs
            print("  Detected Green Mana Gems table (treating as Mana Gems)")
        else:
            currency = "Mana Gems"
        print(f"  Currency: {currency}")
        
        rows = table.find_all('tr')[1:]  # Skip header
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 2:
                item_name = cols[0].text.strip()
                price_text = cols[1].text.strip()
                # Extract numeric price (e.g., "3" from "3 Demonic Mana Gems")
                match = re.match(r'(\d+)', price_text)
                price_num = match.group(1) if match else price_text
                
                scraped_items[item_name] = {"price": price_num, "currency": currency}
                print(f"    Added: {item_name} - {price_num} {currency}")

    print(f"Total unique items scraped: {len(scraped_items)}")

    # Now assign to categories
    for item_name, item_data in scraped_items.items():
        added = False
        # Check predefined first (stays in original tab)
        for category, predefined_items in categories.items():
            if item_name in predefined_items:
                data[category].append({"name": item_name, **item_data})
                print(f"  Assigned predefined: {item_name} to {category}")
                added = True
                break
        
        # If not predefined, add to appropriate tab based on heuristic
        if not added:
            is_equipment = any(keyword in item_name for keyword in equipment_keywords)
            currency = item_data["currency"]
            if currency == "Mana Gems":
                cat = "equipment-mana-gems" if is_equipment else "items-mana-gems"
            else:  # Demonic
                cat = "gear-demonic-mana-gems" if is_equipment else "demonic-mana-gems"
            data[cat].append({"name": item_name, **item_data})
            print(f"  Assigned new/missing: {item_name} to {cat}")

    # Save to JSON
    try:
        with open('mala_kar_items.json', 'w') as f:
            json.dump(data, f, indent=4)
        print("Successfully saved mala_kar_items.json")
    except Exception as e:
        print(f"Error saving JSON: {e}")

    # Touch the file to force a git change (for commit)
    try:
        with open('mala_kar_items.json', 'a'):
            os.utime('mala_kar_items.json', None)
        print("Touched JSON file for git commit")
    except Exception as e:
        print(f"Error touching file: {e}")

if __name__ == "__main__":
    scrape_mala_kar()
