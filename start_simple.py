#!/usr/bin/env python3
"""
Simple startup script for Railway debugging
"""

import os
import sys
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main startup function"""
    try:
        logger.info("Starting simple startup script...")
        
        # Check environment
        port = os.environ.get("PORT", "8000")
        logger.info(f"PORT environment variable: {port}")
        
        # Check Python version
        logger.info(f"Python version: {sys.version}")
        
        # Check current directory
        logger.info(f"Current directory: {os.getcwd()}")
        logger.info(f"Files in directory: {os.listdir('.')}")
        
        # Try to import the app step by step
        logger.info("Testing imports step by step...")
        
        # Test basic imports
        try:
            import fastapi
            logger.info(f"✓ FastAPI {fastapi.__version__}")
        except ImportError as e:
            logger.error(f"✗ FastAPI import failed: {e}")
            traceback.print_exc()
            return 1
        
        try:
            import uvicorn
            logger.info(f"✓ Uvicorn {uvicorn.__version__}")
        except ImportError as e:
            logger.error(f"✗ Uvicorn import failed: {e}")
            traceback.print_exc()
            return 1
        
        # Test local imports
        try:
            import models
            logger.info("✓ models imported")
        except ImportError as e:
            logger.error(f"✗ models import failed: {e}")
            traceback.print_exc()
            return 1
        
        try:
            from auth_operations import get_current_user, require_auth, require_admin
            logger.info("✓ auth_operations imported")
        except ImportError as e:
            logger.error(f"✗ auth_operations import failed: {e}")
            traceback.print_exc()
            return 1
        
        # Try to import the main app
        logger.info("Importing main app...")
        try:
            from main import app
            logger.info("✓ App imported successfully")
        except Exception as e:
            logger.error(f"✗ App import failed: {e}")
            traceback.print_exc()
            return 1
        
        # Start the server
        logger.info(f"Starting server on port {port}...")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=int(port),
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
