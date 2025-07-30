import yfinance as yf
import logging
import pandas as pd
from datetime import datetime
from pandas import Timestamp
from utils import load_stocks, save_stocks, fmt_currency, fmt_percent

def get_stock_with_filters(sector_param, ticker_param, isxticker_param, page, per_page):
    """
    Get stocks with filtering and pagination
    """
    stocks = load_stocks()
    
    # Filter stocks by sector if provided
    filtered_stocks = stocks
    if sector_param:
        filtered_stocks = [stock for stock in stocks if stock.get('sector', '').lower() == sector_param.lower()]
    
    # Filter stocks by ticker if provided
    if ticker_param:
        filtered_stocks = [stock for stock in filtered_stocks if ticker_param.lower() in stock.get('ticker', '').lower()]
    
    # Filter stocks by isxticker if provided
    if isxticker_param is not None:
        isxticker_bool = str(isxticker_param).lower() == 'true'
        filtered_stocks = [stock for stock in filtered_stocks if stock.get('isxticker', False) == isxticker_bool]
    
    # Apply pagination
    total = len(filtered_stocks)
    start = (page - 1) * per_page
    end = start + per_page
    paged_stocks = filtered_stocks[start:end]
    
    return {
        'total': total,
        'page': page,
        'per_page': per_page,
        'results': paged_stocks
    }

def get_stock_details(tickers_param, sector_param, isxticker_param, sort_by=None, sort_order='asc'):
    """
    Get detailed stock information with filtering and sorting
    """
    stocks = load_stocks()

    # Filter stocks by sector if provided
    filtered_stocks = stocks
    if sector_param:
        filtered_stocks = [stock for stock in stocks if stock.get('sector', '').lower() == sector_param]

    # Filter stocks by isxticker if provided
    if isxticker_param is not None:
        isxticker_bool = str(isxticker_param).lower() == 'true'
        filtered_stocks = [stock for stock in filtered_stocks if stock.get('isxticker', False) == isxticker_bool]

    all_symbols = [stock['ticker'] for stock in filtered_stocks]

    if tickers_param:
        requested = [s.strip().lower() for s in tickers_param.split(',') if s.strip()]
        # Case-insensitive exact match
        symbols = [s for s in all_symbols if s.lower() in requested]
        if not symbols:
            return {'results': []}
    else:
        symbols = all_symbols
    results = []
    
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            # Get sector from stock.json instead of Yahoo API
            stock_info = next((stock for stock in stocks if stock['ticker'] == symbol), None)
            sector = stock_info.get('sector', 'N/A') if stock_info else 'N/A'
            
            # Convert MarketCap to millions
            market_cap_raw = info.get('marketCap', 'N/A')
            if market_cap_raw and market_cap_raw != 'N/A':
                try:
                    market_cap_millions = market_cap_raw / 1000000
                    market_cap = f"${market_cap_millions:,.2f}M"
                except (TypeError, ValueError):
                    market_cap = 'N/A'
            else:
                market_cap = 'N/A'
            
            # Format PE as currency with 2 decimal places
            pe_raw = info.get('trailingPE', 'N/A')
            if pe_raw and pe_raw != 'N/A':
                try:
                    pe = fmt_currency(float(pe_raw))
                except (TypeError, ValueError):
                    pe = 'N/A'
            else:
                pe = 'N/A'
            
            # Format NextEarningDate
            next_earning = info.get('earningsTimestamp', None)
            if next_earning and next_earning != 'N/A':
                try:
                    # Convert to pandas Timestamp to handle various datetime formats
                    if isinstance(next_earning, (int, float)):
                        # If it's a numeric timestamp
                        next_earning = Timestamp(next_earning, unit='s').strftime('%Y-%m-%d')
                    else:
                        # If it's already a datetime-like object
                        next_earning = Timestamp(next_earning).strftime('%Y-%m-%d')
                except Exception as e:
                    logging.warning(f"Error formatting earnings date for {symbol}: {e}")
                    next_earning = 'N/A'
            else:
                next_earning = 'N/A'
            
            current_price_raw = info.get('currentPrice', 0)
            current_price = fmt_currency(current_price_raw)
            today_low = fmt_currency(info.get('dayLow', 'N/A'))
            today_high = fmt_currency(info.get('dayHigh', 'N/A'))
            today_pct = fmt_percent(info.get('regularMarketChangePercent', 'N/A'))

            # Previous day data
            prev_day_low = prev_day_high = prev_day_close = prev_day_pct = 'N/A'
            hist = ticker.history(period='1y')
            if not hist.empty and len(hist) >= 2:
                # Get previous trading day data (second to last row)
                prev_day = hist.iloc[-2]
                prev_day_low = fmt_currency(prev_day['Low'])
                prev_day_high = fmt_currency(prev_day['High'])
                prev_day_close = fmt_currency(prev_day['Close'])

                # Calculate percentage change from previous day close to current price
                if current_price_raw and current_price_raw != 'N/A':
                    try:
                        prev_close_raw = prev_day['Close']
                        if prev_close_raw > 0:
                            pct_change = ((current_price_raw - prev_close_raw) / prev_close_raw) * 100
                            prev_day_pct = fmt_percent(round(pct_change, 2))
                    except (TypeError, ValueError):
                        prev_day_pct = 'N/A'

            # Historical data
            five_day_low = five_day_high = five_day_pct = 'N/A'
            one_month_low = one_month_high = one_month_pct = 'N/A'
            six_month_low = six_month_high = six_month_pct = 'N/A'
            one_year_low = one_year_high = one_year_pct = 'N/A'
            if not hist.empty:
                # 5d
                hist_5d = hist.tail(5)
                if not hist_5d.empty:
                    five_day_low = fmt_currency(hist_5d['Low'].min())
                    five_day_high = fmt_currency(hist_5d['High'].max())
                    first = hist_5d['Close'].iloc[0]
                    last = hist_5d['Close'].iloc[-1]
                    five_day_pct = fmt_percent(round(((last - first) / first) * 100, 2))
                # 1mo
                hist_1mo = hist.tail(21)  # ~21 trading days in a month
                if not hist_1mo.empty:
                    one_month_low = fmt_currency(hist_1mo['Low'].min())
                    one_month_high = fmt_currency(hist_1mo['High'].max())
                    first = hist_1mo['Close'].iloc[0]
                    last = hist_1mo['Close'].iloc[-1]
                    one_month_pct = fmt_percent(round(((last - first) / first) * 100, 2))
                # 6mo
                hist_6mo = hist.tail(126)  # ~126 trading days in 6 months
                if not hist_6mo.empty:
                    six_month_low = fmt_currency(hist_6mo['Low'].min())
                    six_month_high = fmt_currency(hist_6mo['High'].max())
                    first = hist_6mo['Close'].iloc[0]
                    last = hist_6mo['Close'].iloc[-1]
                    six_month_pct = fmt_percent(round(((last - first) / first) * 100, 2))
                # 1y
                one_year_low = fmt_currency(hist['Low'].min())
                one_year_high = fmt_currency(hist['High'].max())
                first = hist['Close'].iloc[0]
                last = hist['Close'].iloc[-1]
                one_year_pct = fmt_percent(round(((last - first) / first) * 100, 2))
            else:
                five_day_low = five_day_high = one_month_low = one_month_high = six_month_low = six_month_high = one_year_low = one_year_high = 'N/A'
            
            data = {
                'Sector': sector,
                'Ticker': symbol,
                'MarketCap': market_cap,
                'PE': pe,
                'NextEarningDate': next_earning,
                'CurrentPrice': current_price,
                'TodayLow': today_low,
                'TodayHigh': today_high,
                'TodayPercentageChange': today_pct,
                'PreviousDayLow': prev_day_low,
                'PreviousDayHigh': prev_day_high,
                'PreviousDayClose': prev_day_close,
                'PreviousDayPercentageChange': prev_day_pct,
                'FiveDayLow': five_day_low,
                'FiveDayHigh': five_day_high,
                'FiveDayPercentageChange': five_day_pct,
                'OneMonthLow': one_month_low,
                'OneMonthHigh': one_month_high,
                'OneMonthPercentageChange': one_month_pct,
                'SixMonthLow': six_month_low,
                'SixMonthHigh': six_month_high,
                'SixMonthPercentageChange': six_month_pct,
                'OneYearLow': one_year_low,
                'OneYearHigh': one_year_high,
                'OneYearPercentageChange': one_year_pct
            }
            results.append(data)
        except Exception as e:
            logging.error(f"Error fetching ticker info for symbol: {symbol} | Error: {e}")
            results.append({'Ticker': symbol, 'error': str(e)})
    
    # Sort results if sort_by is provided
    if sort_by and results:
        try:
            # Define sortable columns and their corresponding data keys
            sortable_columns = {
                'NextEarningDate': 'NextEarningDate',
                'TodayPercentageChange': 'TodayPercentageChange',
                'PreviousDayPercentageChange': 'PreviousDayPercentageChange',
                'FiveDayPercentageChange': 'FiveDayPercentageChange',
                'OneMonthPercentageChange': 'OneMonthPercentageChange',
                'SixMonthPercentageChange': 'SixMonthPercentageChange',
                'OneYearPercentageChange': 'OneYearPercentageChange'
            }
            
            if sort_by in sortable_columns:
                key = sortable_columns[sort_by]
                
                def sort_key(item):
                    value = item.get(key, 'N/A')
                    if value == 'N/A':
                        return float('inf') if sort_order == 'asc' else float('-inf')
                    
                    # Extract numeric value from percentage strings
                    if 'PercentageChange' in key:
                        # Remove % and convert to float
                        try:
                            return float(value.replace('%', '').replace('+', ''))
                        except (ValueError, AttributeError):
                            return float('inf') if sort_order == 'asc' else float('-inf')
                    elif key == 'NextEarningDate':
                        # Convert date string to comparable format
                        try:
                            if value == 'N/A':
                                return '9999-12-31' if sort_order == 'asc' else '1900-01-01'
                            return value
                        except:
                            return '9999-12-31' if sort_order == 'asc' else '1900-01-01'
                    else:
                        return value
                
                results.sort(key=sort_key, reverse=(sort_order.lower() == 'desc'))
                
        except Exception as e:
            logging.error(f"Error sorting results: {e}")
    
    return {
        'results': results
    }

def add_stock_to_file(ticker, sector, isxticker):
    """
    Add a new stock to the stocks file
    """
    stocks = load_stocks()
    
    # Check if stock already exists
    if any(s.get('ticker', '').lower() == ticker.lower() for s in stocks):
        return False, "Stock already exists"
    
    stocks.append({
        'ticker': ticker,
        'sector': sector,
        'isxticker': isxticker
    })
    save_stocks(stocks)
    return True, "Stock added successfully"

def update_stock_in_file(old_ticker, sector, isxticker, new_ticker=None):
    """
    Update an existing stock in the stocks file
    """
    logging.info(f"update_stock_in_file called with old_ticker: {old_ticker}, new_ticker: {new_ticker}, sector: {sector}, isxticker: {isxticker}")
    
    stocks = load_stocks()
    logging.info(f"Loaded {len(stocks)} stocks from file")
    
    # Find and update the stock
    found = False
    for s in stocks:
        if s.get('ticker', '').lower() == old_ticker.lower():
            logging.info(f"Found stock to update: {s}")
            
            # Check if new ticker already exists (if we're updating the ticker)
            if new_ticker and new_ticker.lower() != old_ticker.lower():
                if any(existing.get('ticker', '').lower() == new_ticker.lower() for existing in stocks if existing != s):
                    logging.error(f"New ticker '{new_ticker}' already exists")
                    return False, "New ticker already exists"
                s['ticker'] = new_ticker
            
            s['sector'] = sector
            s['isxticker'] = isxticker
            found = True
            logging.info(f"Updated stock: {s}")
            break
    
    if not found:
        logging.error(f"Stock with ticker '{old_ticker}' not found in {len(stocks)} stocks")
        return False, "Stock not found"
    
    try:
        save_stocks(stocks)
        logging.info(f"Successfully saved {len(stocks)} stocks to file")
        return True, "Stock updated successfully"
    except Exception as e:
        logging.error(f"Error saving stocks: {e}")
        return False, f"Error saving: {str(e)}"

def delete_stock_from_file(ticker):
    """
    Delete a stock from the stocks file
    """
    stocks = load_stocks()
    
    # Remove the stock
    new_stocks = [s for s in stocks if s.get('ticker', '').lower() != ticker.lower()]
    
    if len(new_stocks) == len(stocks):
        return False, "Stock not found"
    
    save_stocks(new_stocks)
    return True, "Stock deleted successfully"