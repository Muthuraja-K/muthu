#!/usr/bin/env python3
"""
Test script to verify that the application can start properly
"""

import sys
import os
import traceback

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    # Test basic Python modules
    try:
        import json
        print("✓ json")
    except ImportError as e:
        print(f"✗ json import failed: {e}")
        return False
    
    try:
        import logging
        print("✓ logging")
    except ImportError as e:
        print(f"✗ logging import failed: {e}")
        return False
    
    # Test FastAPI and related modules
    try:
        import fastapi
        print(f"✓ FastAPI {fastapi.__version__}")
    except ImportError as e:
        print(f"✗ FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print(f"✓ Uvicorn {uvicorn.__version__}")
    except ImportError as e:
        print(f"✗ Uvicorn import failed: {e}")
        return False
    
    # Test other required modules
    try:
        import yfinance
        print(f"✓ yfinance {yfinance.__version__}")
    except ImportError as e:
        print(f"✗ yfinance import failed: {e}")
        return False
    
    try:
        import pandas
        print(f"✓ pandas {pandas.__version__}")
    except ImportError as e:
        print(f"✗ pandas import failed: {e}")
        return False
    
    try:
        import requests
        print(f"✓ requests {requests.__version__}")
    except ImportError as e:
        print(f"✗ requests import failed: {e}")
        return False
    
    try:
        import bcrypt
        print("✓ bcrypt")
    except ImportError as e:
        print(f"✗ bcrypt import failed: {e}")
        return False
    
    try:
        import jwt
        print("✓ PyJWT")
    except ImportError as e:
        print(f"✗ PyJWT import failed: {e}")
        return False
    
    # Test local modules
    try:
        from models import LoginRequest, TokenRequest, StockRequest, SectorRequest, UserRequest
        print("✓ models")
    except ImportError as e:
        print(f"✗ models import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        from auth_operations import get_current_user, require_auth, require_admin
        print("✓ auth_operations")
    except ImportError as e:
        print(f"✗ auth_operations import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        from stock_operations import get_stock_details
        print("✓ stock_operations")
    except ImportError as e:
        print(f"✗ stock_operations import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        from enhanced_stock_operations import get_enhanced_stock_details
        print("✓ enhanced_stock_operations")
    except ImportError as e:
        print(f"✗ enhanced_stock_operations import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        from history_cache import history_cache
        print("✓ history_cache")
    except ImportError as e:
        print(f"✗ history_cache import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        from stock_summary import get_stock_summary
        print("✓ stock_summary")
    except ImportError as e:
        print(f"✗ stock_summary import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        from sector_operations import get_sectors_with_filters
        print("✓ sector_operations")
    except ImportError as e:
        print(f"✗ sector_operations import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        from user_operations import get_users_with_filters
        print("✓ user_operations")
    except ImportError as e:
        print(f"✗ user_operations import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        from earning_summary import get_earning_summary
        print("✓ earning_summary")
    except ImportError as e:
        print(f"✗ earning_summary import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        from sentiment_analysis import get_sentiment_analysis
        print("✓ sentiment_analysis")
    except ImportError as e:
        print(f"✗ sentiment_analysis import failed: {e}")
        traceback.print_exc()
        return False
    
    # Test main app import
    try:
        from main import app
        print("✓ Main app imported successfully")
    except ImportError as e:
        print(f"✗ Main app import failed: {e}")
        traceback.print_exc()
        return False
    
    return True

def main():
    """Main test function"""
    print("=== Stock Prediction API Startup Test ===")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Files in directory: {os.listdir('.')}")
    
    if test_imports():
        print("\n✅ All imports successful! Application should start properly.")
        return 0
    else:
        print("\n❌ Import test failed! Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
