import yfinance as yf
import logging
import pandas as pd
from datetime import datetime, timedelta
from pandas import Timestamp
from utils import load_stocks, fmt_currency, fmt_percent, convert_ui_date_to_iso
import concurrent.futures
from typing import List, Dict, Any, Tuple

def process_single_stock_summary(stock: Dict, date_from_iso: str, date_to_iso: str, sector: str) -> Dict[str, Any]:
    """
    Process a single stock to get its summary information
    This function will be called in parallel
    """
    try:
        ticker = yf.Ticker(stock['ticker'])
        info = ticker.info
        
        # Determine the date range for historical data
        if date_from_iso and date_to_iso:
            # Both dates provided - use exact range
            start_date = Timestamp(date_from_iso)
            end_date = Timestamp(date_to_iso)
            buffer_end = end_date + timedelta(days=1)
            hist = ticker.history(start=start_date, end=buffer_end)
        elif date_from_iso:
            # Only start date provided
            start_date = Timestamp(date_from_iso)
            buffer_start = start_date - timedelta(days=5)
            hist = ticker.history(start=buffer_start)
        elif date_to_iso:
            # Only end date provided
            end_date = Timestamp(date_to_iso)
            buffer_end = end_date + timedelta(days=5)
            hist = ticker.history(end=buffer_end)
        else:
            # No dates provided - use last year
            hist = ticker.history(period='1y')

        if hist.empty:
            return None

        current_price = info.get('currentPrice', 0)
        if not current_price or current_price <= 0:
            return None

        # Get start date closing price (first date in filtered range)
        start_date_close_price = hist['Close'].iloc[0] if not hist.empty else 0
        
        # Get end date closing price (last date in filtered range)
        end_date_close_price = hist['Close'].iloc[-1] if not hist.empty else 0

        # Calculate percentage change based on start and end closing prices
        percentage_change = 0
        if start_date_close_price > 0 and end_date_close_price > 0:
            percentage_change = ((end_date_close_price - start_date_close_price) / start_date_close_price) * 100

        return {
            'ticker': stock['ticker'],
            'currentPrice': fmt_currency(current_price),
            'startDateClosePrice': fmt_currency(start_date_close_price),
            'endDateClosePrice': fmt_currency(end_date_close_price),
            'percentageChange': fmt_percent(round(percentage_change, 2)),
            'sector': sector,
            'isxticker': stock.get('isxticker', False),
            'raw_percentage': percentage_change  # For calculating averages
        }

    except Exception as e:
        logging.error(f"Error processing stock {stock['ticker']}: {e}")
        return None

def process_sector_stocks(sector_stocks: List[Dict], date_from_iso: str, date_to_iso: str, sector: str) -> Tuple[str, List[Dict], float]:
    """
    Process all stocks in a sector using parallel processing
    Returns: (sector_name, stock_data_list, total_percentage)
    """
    if not sector_stocks:
        return sector, [], 0

    # Process stocks in parallel
    max_workers = min(10, len(sector_stocks))  # Limit concurrent requests
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks for this sector
        future_to_stock = {
            executor.submit(process_single_stock_summary, stock, date_from_iso, date_to_iso, sector): stock 
            for stock in sector_stocks
        }
        
        # Collect results as they complete
        sector_data = []
        total_percentage = 0
        valid_percentages = 0
        
        for future in concurrent.futures.as_completed(future_to_stock):
            stock = future_to_stock[future]
            try:
                result = future.result()
                if result is not None:
                    sector_data.append(result)
                    if 'raw_percentage' in result:
                        total_percentage += result['raw_percentage']
                        valid_percentages += 1
                        # Remove raw_percentage from final result
                        del result['raw_percentage']
                    logging.info(f"Completed processing for {stock['ticker']} in sector {sector}")
            except Exception as e:
                logging.error(f"Exception occurred while processing {stock['ticker']}: {e}")
                continue

    return sector, sector_data, total_percentage if valid_percentages > 0 else 0

def get_stock_summary(sectors_param, isxticker_param, date_from_param, date_to_param):
    """
    Get stock summary grouped by sectors with filtering and date range support
    Now uses parallel processing for better performance
    """
    stocks = load_stocks()

    # Convert UI date format to ISO format
    date_from_iso = convert_ui_date_to_iso(date_from_param)
    date_to_iso = convert_ui_date_to_iso(date_to_param)
    
    logging.info(f"Date validation: from='{date_from_param}' -> '{date_from_iso}', to='{date_to_param}' -> '{date_to_iso}'")

    # Filter stocks by sectors if provided
    filtered_stocks = stocks
    if sectors_param:
        requested_sectors = [s.strip().lower() for s in sectors_param.split(',') if s.strip()]
        filtered_stocks = [stock for stock in stocks if stock.get('sector', '').lower() in requested_sectors]

    # Filter stocks by isxticker if provided
    if isxticker_param is not None:
        isxticker_bool = str(isxticker_param).lower() == 'true'
        filtered_stocks = [stock for stock in filtered_stocks if stock.get('isxticker', False) == isxticker_bool]

    # Group stocks by sector
    sector_groups = {}
    for stock in filtered_stocks:
        sector = stock.get('sector', 'Unknown')
        if sector not in sector_groups:
            sector_groups[sector] = []
        sector_groups[sector].append(stock)

    # Process each sector group in parallel
    results = []
    max_sector_workers = min(5, len(sector_groups))  # Limit concurrent sectors
    
    logging.info(f"Processing {len(sector_groups)} sectors with {max_sector_workers} workers")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_sector_workers) as executor:
        # Submit all sector processing tasks
        future_to_sector = {
            executor.submit(process_sector_stocks, sector_stocks, date_from_iso, date_to_iso, sector): sector 
            for sector, sector_stocks in sector_groups.items()
        }
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_sector):
            sector = future_to_sector[future]
            try:
                sector_name, sector_data, total_percentage = future.result()
                
                if sector_data:
                    # Calculate average percentage for the sector
                    valid_percentages = len([s for s in sector_data if 'percentageChange' in s])
                    average_percentage = '0%'
                    if valid_percentages > 0:
                        avg_pct = total_percentage / valid_percentages
                        average_percentage = fmt_percent(round(avg_pct, 2))

                    sector_result = {
                        'sector': sector_name,
                        'averagePercentage': average_percentage,
                        'stocks': sector_data
                    }
                    results.append(sector_result)
                    logging.info(f"Completed processing sector {sector_name} with {len(sector_data)} stocks")
                    
            except Exception as e:
                logging.error(f"Exception occurred while processing sector {sector}: {e}")
                continue

    return results