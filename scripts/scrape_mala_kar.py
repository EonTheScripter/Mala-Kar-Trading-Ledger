import requests
from bs4 import BeautifulSoup
import json

def scrape_mala_kar():
    url = "https://wiki.ironco.re/index.php?title=Mala%27kar"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching page: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Define categories based on your HTML structure
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

    # Find all tables
    tables = soup.find_all('table')
    for table in tables:
        currency = "Mana Gems" if "Mana Gems" in table.text else "Demonic Mana Gems"
        rows = table.find_all('tr')[1:]  # Skip header

        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 2:
                item_name = cols[0].text.strip()
                price = cols[1].text.strip()

                # Find which category the item belongs to
                for category, items in categories.items():
                    if item_name in items:
                        data[category].append({"name": item_name, "price": price, "currency": currency})
                    # Add missing items to the correct category based on currency
                    elif currency == "Mana Gems" and category in ["equipment-mana-gems", "items-mana-gems"]:
                        if item_name not in items:
                            data[category].append({"name": item_name, "price": price, "currency": currency})
                    elif currency == "Demonic Mana Gems" and category in ["gear-demonic-mana-gems", "demonic-mana-gems"]:
                        if item_name not in items:
                            data[category].append({"name": item_name, "price": price, "currency": currency})

    # Save to JSON
    with open('mala_kar_items.json', 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    scrape_mala_kar()
