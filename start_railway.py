#!/usr/bin/env python3
"""
Railway startup script for Stock Prediction API
"""

import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed"""
    logger.info("Checking dependencies...")
    
    try:
        import fastapi
        logger.info(f"✓ FastAPI {fastapi.__version__}")
    except ImportError as e:
        logger.error(f"✗ FastAPI not found: {e}")
        return False
    
    try:
        import uvicorn
        logger.info(f"✓ Uvicorn {uvicorn.__version__}")
    except ImportError as e:
        logger.error(f"✗ Uvicorn not found: {e}")
        return False
    
    return True

def start_application():
    """Start the FastAPI application"""
    logger.info("Starting Stock Prediction API...")
    
    # Get port from environment variable
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Using port: {port}")
    
    # Import and run the application
    try:
        from main import app
        import uvicorn
        
        logger.info("Application imported successfully")
        logger.info(f"Starting server on 0.0.0.0:{port}")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    logger.info("Railway startup script initiated")
    
    # Check dependencies
    if not check_dependencies():
        logger.error("Dependency check failed")
        sys.exit(1)
    
    # Start the application
    start_application()
