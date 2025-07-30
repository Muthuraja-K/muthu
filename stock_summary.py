import yfinance as yf
import logging
import pandas as pd
from datetime import datetime, timedelta
from pandas import Timestamp
from utils import load_stocks, fmt_currency, fmt_percent, convert_ui_date_to_iso

def get_stock_summary(sectors_param, isxticker_param, date_from_param, date_to_param):
    """
    Get stock summary grouped by sectors with filtering and date range support
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

    # Process each sector group
    results = []
    for sector, sector_stocks in sector_groups.items():
        sector_data = []
        total_percentage = 0
        valid_percentages = 0

        for stock in sector_stocks:
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
                    continue
                current_price = info.get('currentPrice', 0)
                if current_price and current_price > 0:
                    # Get start date closing price (first date in filtered range)
                    start_date_close_price = hist['Close'].iloc[0] if not hist.empty else 0
                    
                    # Get end date closing price (last date in filtered range)
                    end_date_close_price = hist['Close'].iloc[-1] if not hist.empty else 0

                    # Calculate percentage change based on start and end closing prices
                    percentage_change = 0
                    if start_date_close_price > 0 and end_date_close_price > 0:
                        percentage_change = ((end_date_close_price - start_date_close_price) / start_date_close_price) * 100
                        total_percentage += percentage_change
                        valid_percentages += 1

                    stock_data = {
                        'ticker': stock['ticker'],
                        'currentPrice': fmt_currency(current_price),
                        'startDateClosePrice': fmt_currency(start_date_close_price),
                        'endDateClosePrice': fmt_currency(end_date_close_price),
                        'percentageChange': fmt_percent(round(percentage_change, 2)),
                        'sector': sector,
                        'isxticker': stock.get('isxticker', False)
                    }
                    sector_data.append(stock_data)

            except Exception as e:
                logging.error(f"Error processing stock {stock['ticker']}: {e}")
                continue

        # Calculate average percentage for the sector
        average_percentage = '0%'
        if valid_percentages > 0:
            avg_pct = total_percentage / valid_percentages
            average_percentage = fmt_percent(round(avg_pct, 2))

        if sector_data:
            sector_result = {
                'sector': sector,
                'averagePercentage': average_percentage,
                'stocks': sector_data
            }
            results.append(sector_result)

    return results