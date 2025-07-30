import json
import os

stock_path = 'stock.json'
sector_path = 'sector.json'

# Load all sectors from stock.json
with open(stock_path, 'r') as f:
    stocks = json.load(f)
unique_sectors = {x['sector'] for x in stocks if x.get('sector') and x['sector'] != 'N/A'}

# Load existing sectors from sector.json
if os.path.exists(sector_path):
    with open(sector_path, 'r') as f:
        existing = json.load(f)
    existing_sectors = {x['sector'] for x in existing}
else:
    existing_sectors = set()

# Combine and sort
all_sectors = sorted(unique_sectors | existing_sectors)

# Write back to sector.json
with open(sector_path, 'w') as f:
    json.dump([{'sector': x} for x in all_sectors], f, indent=2) 