from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any
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
from models import (
    LoginRequest, TokenRequest, StockRequest, StockUpdateRequest, StockDeleteRequest,
    SectorRequest, SectorUpdateRequest, SectorDeleteRequest,
    UserRequest, UserUpdateRequest, UserDeleteRequest
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Application startup event
@app.on_event("startup")
async def startup_event():
    logging.info("Stock Prediction API started successfully!")

@app.get("/")
async def serve_frontend():
    return FileResponse("static/index.html")

# Authentication endpoints
@app.post('/api/login')
async def login_route(request: LoginRequest):
    result = login_user(request.username, request.password)
    
    if result['success']:
        return result
    else:
        raise HTTPException(status_code=401, detail=result)

@app.post('/api/verify-token')
async def verify_token_route(request: TokenRequest):
    from auth_operations import verify_token
    
    payload = verify_token(request.token)
    if payload:
        return {
            'valid': True,
            'username': payload['username'],
            'role': payload['role'],
            'firstname': payload.get('firstname', ''),
            'lastname': payload.get('lastname', '')
        }
    else:
        raise HTTPException(status_code=401, detail={'valid': False})

# Protected routes - require authentication
@app.get('/api/getstock')
async def get_stock_route(
    sector: str = "",
    ticker: str = "",
    isxticker: Optional[bool] = None,
    page: int = 1,
    per_page: int = 10,
    current_user: Dict[str, Any] = Depends(require_auth)
):
    sector_param = sector.strip().lower()
    ticker_param = ticker.strip().lower()
    
    result = get_stock_with_filters(sector_param, ticker_param, isxticker, page, per_page)
    
    # Always include isxticker in results
    for s in result['results']:
        if 'isxticker' not in s:
            s['isxticker'] = False
    
    return result

@app.get('/api/getstockdetails')
async def get_stockdetails_route(
    ticker: str = "",
    sector: str = "",
    isxticker: Optional[bool] = None,
    sort_by: Optional[str] = None,
    sort_order: str = "asc",
    page: int = 1,
    per_page: int = 50,
    current_user: Dict[str, Any] = Depends(require_auth)
):
    tickers_param = ticker.strip()
    sector_param = sector.strip().lower()
    
    result = get_stock_details(tickers_param, sector_param, isxticker, sort_by, sort_order, page, per_page)
    return result

# Admin-only routes
@app.post('/api/stocks')
async def add_stock_route(
    request: StockRequest,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    success, message = add_stock_to_file(request.ticker, request.sector, request.isxticker)
    
    if success:
        return {
            'message': message, 
            'stock': {
                'ticker': request.ticker, 
                'sector': request.sector, 
                'isxticker': request.isxticker
            }
        }
    else:
        raise HTTPException(status_code=400, detail={'error': message})

@app.put('/api/stocks/update')
async def update_stock_route(
    request: StockUpdateRequest,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    logging.info(f"Updating stock")
    logging.info(f"Request data: {request.dict()}")
    
    new_ticker = request.ticker if request.ticker else request.oldTicker
    
    logging.info(f"Updating stock {request.oldTicker} to {new_ticker} with sector: {request.sector}, isxticker: {request.isxticker}")
    
    success, message = update_stock_in_file(request.oldTicker, request.sector, request.isxticker, new_ticker)
    
    logging.info(f"Update result: success={success}, message={message}")
    
    if success:
        return {
            'message': message, 
            'stock': {
                'ticker': new_ticker, 
                'sector': request.sector, 
                'isxticker': request.isxticker
            }
        }
    else:
        raise HTTPException(status_code=404, detail={'error': message})

@app.post('/api/stocks/delete')
async def delete_stock_route(
    request: StockDeleteRequest,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    success, message = delete_stock_from_file(request.ticker)
    
    if success:
        return {'message': message, 'ticker': request.ticker}
    else:
        raise HTTPException(status_code=404, detail={'error': message})

@app.get('/api/sectors')
async def get_sectors_route(
    filter: str = "",
    page: int = 1,
    per_page: int = 10,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    filter_param = filter.strip().lower()
    result = get_sectors_with_filters(filter_param, page, per_page)
    return result

@app.post('/api/sectors')
async def add_sector_route(
    request: SectorRequest,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    success, message = add_sector_to_file(request.sector)
    
    if success:
        return {'message': message, 'sector': request.sector}
    else:
        raise HTTPException(status_code=400, detail={'error': message})

@app.put('/api/sectors/update')
async def update_sector_route(
    request: SectorUpdateRequest,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    success, message = update_sector_in_file(request.oldSector, request.newSector)
    
    if success:
        return {'message': message, 'sector': request.newSector}
    else:
        raise HTTPException(status_code=404, detail={'error': message})

@app.post('/api/sectors/delete')
async def delete_sector_route(
    request: SectorDeleteRequest,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    success, message = delete_sector_from_file(request.sector)
    
    if success:
        return {'message': message, 'sector': request.sector}
    else:
        raise HTTPException(status_code=404, detail={'error': message})

# User management endpoints
@app.get('/api/users')
async def get_users_route(
    filter: str = "",
    page: int = 1,
    per_page: int = 10,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    username_param = filter.strip().lower()
    result = get_users_with_filters(username_param, page, per_page)
    return result

@app.post('/api/users')
async def add_user_route(
    request: UserRequest,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    success, message = add_user_to_file(
        request.username, 
        request.password, 
        request.role, 
        request.firstname, 
        request.lastname
    )
    
    if success:
        return {
            'message': message, 
            'user': {
                'username': request.username, 
                'role': request.role, 
                'firstname': request.firstname, 
                'lastname': request.lastname
            }
        }
    else:
        raise HTTPException(status_code=400, detail={'error': message})

@app.put('/api/users/update')
async def update_user_route(
    request: UserUpdateRequest,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    success, message = update_user_in_file(
        request.oldUsername, 
        request.username, 
        request.password, 
        request.role, 
        request.firstname, 
        request.lastname
    )
    
    if success:
        return {
            'message': message, 
            'user': {
                'username': request.username, 
                'role': request.role, 
                'firstname': request.firstname, 
                'lastname': request.lastname
            }
        }
    else:
        raise HTTPException(status_code=404, detail={'error': message})

@app.post('/api/users/delete')
async def delete_user_route(
    request: UserDeleteRequest,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    success, message = delete_user_from_file(request.username)
    
    if success:
        return {'message': message, 'username': request.username}
    else:
        raise HTTPException(status_code=404, detail={'error': message})

# User-accessible routes
@app.get('/api/stock-summary')
async def get_stock_summary_route(
    sectors: str = "",
    isxticker: Optional[bool] = None,
    date_from: str = "",
    date_to: str = "",
    current_user: Dict[str, Any] = Depends(require_auth)
):
    sectors_param = sectors.strip()
    date_from_param = date_from.strip()
    date_to_param = date_to.strip()
    
    results = get_stock_summary(sectors_param, isxticker, date_from_param, date_to_param)
    
    return {'groups': results}

@app.get('/api/earning-summary')
async def get_earning_summary_route(
    sectors: str = "",
    date_from: str = "",
    date_to: str = "",
    page: int = 1,
    per_page: int = 10,
    current_user: Dict[str, Any] = Depends(require_auth)
):
    sectors_param = sectors.strip()
    date_from_param = date_from.strip()
    date_to_param = date_to.strip()
    
    result = get_earning_summary(sectors_param, date_from_param, date_to_param, page, per_page)
    return result

# Download endpoints
@app.get('/api/download/{file_type}')
async def download_file_route(
    file_type: str,
    current_user: Dict[str, Any] = Depends(require_auth)
):
    """Download JSON files based on file type"""
    try:
        if file_type == 'users':
            # Only admin can download users file
            if current_user.get('role') != 'admin':
                raise HTTPException(status_code=403, detail={'error': 'Admin access required'})
            
            with open('user.json', 'r') as file:
                data = json.load(file)
            
            # Remove password hashes for security
            for user in data:
                if 'password' in user:
                    del user['password']
            
            return data
            
        elif file_type == 'stocks':
            # Load stocks data
            stocks = load_stocks()
            return stocks
            
        elif file_type == 'sectors':
            # Load sectors data
            sectors = load_sectors()
            return sectors
            
        else:
            raise HTTPException(status_code=400, detail={'error': 'Invalid file type'})
            
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail={'error': 'File not found'})
    except Exception as e:
        raise HTTPException(status_code=500, detail={'error': str(e)})

# Sentiment Analysis endpoint
@app.get('/api/sentiment/{ticker}')
async def get_sentiment_route(
    ticker: str,
    current_user: Dict[str, Any] = Depends(require_auth)
):
    """Get sentiment analysis for a specific ticker"""
    try:
        if not ticker or ticker.strip() == '':
            raise HTTPException(status_code=400, detail={'error': 'Ticker is required'})
        
        ticker = ticker.strip().upper()
        sentiment_data = get_sentiment_analysis(ticker)
        
        return sentiment_data
        
    except Exception as e:
        logging.error(f"Error getting sentiment for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail={'error': 'Failed to get sentiment data'})

# Catch-all route for static files - must be at the end
@app.get("/{path:path}")
async def serve_static(path: str):
    file_path = os.path.join("static", path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    else:
        return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 