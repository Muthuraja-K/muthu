#!/usr/bin/env python3
"""
Development server with auto-reload functionality
Run this script for development with automatic code reloading
"""

import uvicorn
import os
import sys

def main():
    """Start the development server with auto-reload"""
    
    # Add current directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Development server configuration
    config = {
        "app": "main:app",  # Import the app from main.py
        "host": "0.0.0.0",
        "port": 8000,
        "reload": True,  # Enable auto-reload
        "reload_dirs": [".", ".."],  # Watch current and parent directories
        "reload_excludes": [
            "*.pyc", 
            "__pycache__", 
            "*.log", 
            "*.json",
            "*.csv",
            "*.xlsx",
            "static/*",
            "node_modules/*"
        ],
        "log_level": "info",
        "access_log": True,
        "use_colors": True,
        "workers": 1,  # Single worker for development
    }
    
    print("🚀 Starting Stock Prediction API Development Server...")
    print("📁 Auto-reload enabled - watching for file changes")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔄 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        uvicorn.run(**config)
    except KeyboardInterrupt:
        print("\n🛑 Development server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
