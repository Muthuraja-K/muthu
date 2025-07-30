import logging
from datetime import datetime

def fmt_currency(val):
    try:
        f = float(val)
        return f"${f:,.2f}"
    except Exception:
        return val

def fmt_percent(val):
    try:
        f = float(val)
        return f"{f:.2f}%"
    except Exception:
        return val

def convert_ui_date_to_iso(ui_date):
    """
    Convert UI date format (YYYY-MM-DD) to ISO format (YYYY-MM-DD)
    Since UI now sends ISO format, this function validates and returns the same format
    """
    if not ui_date or ui_date.strip() == '':
        return None
    
    try:
        # Parse YYYY-MM-DD format (ISO format)
        date_obj = datetime.strptime(ui_date.strip(), '%Y-%m-%d')
        # Return the same format (already in ISO format)
        return date_obj.strftime('%Y-%m-%d')
    except ValueError as e:
        logging.warning(f"Invalid date format '{ui_date}': {e}")
        return None

def load_stocks():
    import json
    import os
    stock_path = 'stock.json'
    if not os.path.exists(stock_path):
        return []
    with open(stock_path, 'r') as f:
        return json.load(f)

def save_stocks(stocks):
    import json
    import os
    stock_path = 'stock.json'
    try:
        with open(stock_path, 'w') as f:
            json.dump(stocks, f, indent=2)
        logging.info(f"Successfully saved {len(stocks)} stocks to {stock_path}")
    except Exception as e:
        logging.error(f"Error saving stocks to {stock_path}: {e}")
        raise e

def load_sectors():
    import json
    import os
    sector_path = 'sector.json'
    if not os.path.exists(sector_path):
        return []
    with open(sector_path, 'r') as f:
        return json.load(f)

def save_sectors(sectors):
    import json
    sector_path = 'sector.json'
    with open(sector_path, 'w') as f:
        json.dump(sectors, f, indent=2)

def load_users():
    import json
    import os
    user_path = 'user.json'
    if not os.path.exists(user_path):
        return []
    with open(user_path, 'r') as f:
        return json.load(f)

def save_users(users):
    import json
    user_path = 'user.json'
    with open(user_path, 'w') as f:
        json.dump(users, f, indent=2) 