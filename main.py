from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import yfinance as yf
import json
import logging
import os
import sys
from utils import load_stocks, save_stocks, load_sectors, save_sectors, fmt_currency, fmt_percent
from stock_summary import get_stock_summary
from earning_summary import get_earning_summary
from sector_operations import get_sectors_with_filters, add_sector_to_file, update_sector_in_file, delete_sector_from_file
from user_operations import get_users_with_filters, add_user_to_file, update_user_in_file, delete_user_from_file
from stock_operations import get_stock_with_filters, get_stock_details, add_stock_to_file, update_stock_in_file, delete_stock_from_file
from auth_operations import login_user, require_auth, require_admin, create_default_users
from sentiment_analysis import get_sentiment_analysis


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')


app = Flask(__name__, static_folder='static')
CORS(app)

# Create default users on startup
create_default_users()

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    file_path = os.path.join(app.static_folder, path)
    if path != "" and os.path.exists(file_path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")


def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)




# Authentication endpoints
@app.route('/api/login', methods=['POST'])
def login_route():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'username and password are required'}), 400
    
    username = data['username']
    password = data['password']
    
    result = login_user(username, password)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 401

@app.route('/api/verify-token', methods=['POST'])
def verify_token_route():
    data = request.get_json()
    if not data or 'token' not in data:
        return jsonify({'error': 'token is required'}), 400
    
    token = data['token']
    from auth_operations import verify_token
    
    payload = verify_token(token)
    if payload:
        return jsonify({
            'valid': True,
            'username': payload['username'],
            'role': payload['role'],
            'firstname': payload.get('firstname', ''),
            'lastname': payload.get('lastname', '')
        })
    else:
        return jsonify({'valid': False}), 401

# Protected routes - require authentication
@app.route('/api/getstock', methods=['GET'])
@require_auth
def get_stock_route():
  
    sector_param = request.args.get('sector', '').strip().lower()
    ticker_param = request.args.get('ticker', '').strip().lower()
    isxticker_param = request.args.get('isxticker', None)
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    
    result = get_stock_with_filters(sector_param, ticker_param, isxticker_param, page, per_page)
    
    # Always include isxticker in results
    for s in result['results']:
        if 'isxticker' not in s:
            s['isxticker'] = False
    
   
    
    return jsonify(result)

@app.route('/api/getstockdetails', methods=['GET'])
@require_auth
def get_stockdetails_route():
    tickers_param = request.args.get('ticker', '').strip()
    sector_param = request.args.get('sector', '').strip().lower()
    isxticker_param = request.args.get('isxticker', None)
    sort_by = request.args.get('sort_by', None)
    sort_order = request.args.get('sort_order', 'asc')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    
    result = get_stock_details(tickers_param, sector_param, isxticker_param, sort_by, sort_order, page, per_page)
    return jsonify(result)

# Admin-only routes
@app.route('/api/stocks', methods=['POST'])
@require_admin
def add_stock_route():
    data = request.get_json()
    if not data or 'ticker' not in data or 'sector' not in data:
        return jsonify({'error': 'ticker and sector are required'}), 400
    
    ticker = data['ticker']
    sector = data['sector']
    isxticker = data.get('isxticker', False)
    
    success, message = add_stock_to_file(ticker, sector, isxticker)
    
    if success:
        return jsonify({'message': message, 'stock': {'ticker': ticker, 'sector': sector, 'isxticker': isxticker}}), 201
    else:
        return jsonify({'error': message}), 400

@app.route('/api/stocks/update', methods=['PUT'])
@require_admin
def update_stock_route():
    logging.info(f"Updating stock")
    logging.info(f"Request data: {request.get_json()}")
    
    data = request.get_json()
    if not data or 'oldTicker' not in data or 'sector' not in data:
        logging.error(f"Invalid request data: {data}")
        return jsonify({'error': 'oldTicker and sector are required'}), 400
    
    old_ticker = data['oldTicker']
    new_ticker = data.get('ticker', old_ticker)  # Use new ticker if provided, otherwise keep old ticker
    sector = data['sector']
    isxticker = data.get('isxticker', False)
    
    logging.info(f"Updating stock {old_ticker} to {new_ticker} with sector: {sector}, isxticker: {isxticker}")
    
    success, message = update_stock_in_file(old_ticker, sector, isxticker, new_ticker)
    
    logging.info(f"Update result: success={success}, message={message}")
    
    if success:
        return jsonify({'message': message, 'stock': {'ticker': new_ticker, 'sector': sector, 'isxticker': isxticker}})
    else:
        return jsonify({'error': message}), 404

@app.route('/api/stocks/delete', methods=['POST'])
@require_admin
def delete_stock_route():
    data = request.get_json()
    if not data or 'ticker' not in data:
        return jsonify({'error': 'ticker is required'}), 400
    
    ticker = data['ticker']
    success, message = delete_stock_from_file(ticker)
    
    if success:
        return jsonify({'message': message, 'ticker': ticker})
    else:
        return jsonify({'error': message}), 404

@app.route('/api/sectors', methods=['GET'])
@require_admin
def get_sectors_route():
    filter_param = request.args.get('filter', '').strip().lower()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    result = get_sectors_with_filters(filter_param, page, per_page)
    return jsonify(result)

@app.route('/api/sectors', methods=['POST'])
@require_admin
def add_sector_route():
    data = request.get_json()
    if not data or 'sector' not in data:
        return jsonify({'error': 'sector is required'}), 400
    
    success, message = add_sector_to_file(data['sector'])
    
    if success:
        return jsonify({'message': message, 'sector': data['sector']}), 201
    else:
        return jsonify({'error': message}), 400

@app.route('/api/sectors/update', methods=['PUT'])
@require_admin
def update_sector_route():
    data = request.get_json()
    if not data or 'oldSector' not in data or 'newSector' not in data:
        return jsonify({'error': 'oldSector and newSector are required'}), 400
    
    old_sector = data['oldSector']
    new_sector = data['newSector']
    
    success, message = update_sector_in_file(old_sector, new_sector)
    
    if success:
        return jsonify({'message': message, 'sector': new_sector})
    else:
        return jsonify({'error': message}), 404

@app.route('/api/sectors/delete', methods=['POST'])
@require_admin
def delete_sector_route():
    data = request.get_json()
    if not data or 'sector' not in data:
        return jsonify({'error': 'sector is required'}), 400
    
    sector = data['sector']
    success, message = delete_sector_from_file(sector)
    
    if success:
        return jsonify({'message': message, 'sector': sector})
    else:
        return jsonify({'error': message}), 404

# User management endpoints
@app.route('/api/users', methods=['GET'])
@require_admin
def get_users_route():
    username_param = request.args.get('filter', '').strip().lower()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    result = get_users_with_filters(username_param, page, per_page)
    return jsonify(result)

@app.route('/api/users', methods=['POST'])
@require_admin
def add_user_route():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data or 'role' not in data or 'firstname' not in data or 'lastname' not in data:
        return jsonify({'error': 'username, password, role, firstname, and lastname are required'}), 400
    
    username = data['username']
    password = data['password']
    role = data['role']
    firstname = data['firstname']
    lastname = data['lastname']
    
    success, message = add_user_to_file(username, password, role, firstname, lastname)
    
    if success:
        return jsonify({'message': message, 'user': {'username': username, 'role': role, 'firstname': firstname, 'lastname': lastname}}), 201
    else:
        return jsonify({'error': message}), 400

@app.route('/api/users/update', methods=['PUT'])
@require_admin
def update_user_route():
    data = request.get_json()
    if not data or 'oldUsername' not in data or 'username' not in data or 'role' not in data or 'firstname' not in data or 'lastname' not in data:
        return jsonify({'error': 'oldUsername, username, role, firstname, and lastname are required'}), 400
    
    old_username = data['oldUsername']
    username = data['username']
    password = data.get('password', '')  # Optional for updates
    role = data['role']
    firstname = data['firstname']
    lastname = data['lastname']
    
    success, message = update_user_in_file(old_username, username, password, role, firstname, lastname)
    
    if success:
        return jsonify({'message': message, 'user': {'username': username, 'role': role, 'firstname': firstname, 'lastname': lastname}})
    else:
        return jsonify({'error': message}), 404

@app.route('/api/users/delete', methods=['POST'])
@require_admin
def delete_user_route():
    data = request.get_json()
    if not data or 'username' not in data:
        return jsonify({'error': 'username is required'}), 400
    
    username = data['username']
    success, message = delete_user_from_file(username)
    
    if success:
        return jsonify({'message': message, 'username': username})
    else:
        return jsonify({'error': message}), 404

# User-accessible routes
@app.route('/api/stock-summary', methods=['GET'])
@require_auth
def get_stock_summary_route():
    sectors_param = request.args.get('sectors', '').strip()
    isxticker_param = request.args.get('isxticker', None)
    date_from_param = request.args.get('date_from', '').strip()
    date_to_param = request.args.get('date_to', '').strip()
    
    results = get_stock_summary(sectors_param, isxticker_param, date_from_param, date_to_param)
    
    return jsonify({
        'groups': results
    })

@app.route('/api/earning-summary', methods=['GET'])
@require_auth
def get_earning_summary_route():
    sectors_param = request.args.get('sectors', '').strip()
    date_from_param = request.args.get('date_from', '').strip()
    date_to_param = request.args.get('date_to', '').strip()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    result = get_earning_summary(sectors_param, date_from_param, date_to_param, page, per_page)
    return jsonify(result)

# Download endpoints
@app.route('/api/download/<file_type>', methods=['GET'])
@require_auth
def download_file_route(file_type):
    """Download JSON files based on file type"""
    try:
        if file_type == 'users':
            # Only admin can download users file
            if request.user.get('role') != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            
            with open('user.json', 'r') as file:
                data = json.load(file)
            
            # Remove password hashes for security
            for user in data:
                if 'password' in user:
                    del user['password']
            
            return jsonify(data)
            
        elif file_type == 'stocks':
            # Load stocks data
            stocks = load_stocks()
            return jsonify(stocks)
            
        elif file_type == 'sectors':
            # Load sectors data
            sectors = load_sectors()
            return jsonify(sectors)
            
        else:
            return jsonify({'error': 'Invalid file type'}), 400
            
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Sentiment Analysis endpoint
@app.route('/api/sentiment/<ticker>', methods=['GET'])
@require_auth
def get_sentiment_route(ticker):
    """Get sentiment analysis for a specific ticker"""
    try:
        if not ticker or ticker.strip() == '':
            return jsonify({'error': 'Ticker is required'}), 400
        
        ticker = ticker.strip().upper()
        sentiment_data = get_sentiment_analysis(ticker)
        
        return jsonify(sentiment_data)
        
    except Exception as e:
        logging.error(f"Error getting sentiment for {ticker}: {str(e)}")
        return jsonify({'error': 'Failed to get sentiment data'}), 500
#app.run(debug=True) 