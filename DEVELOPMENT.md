# Development Guide - Auto-Reload Setup

## 🚀 Quick Start with Auto-Reload

### Option 1: Using the Development Server Script (Recommended)
```bash
# Navigate to the StockWebApi directory
cd StockWebApi

# Start the development server with auto-reload
python dev_server.py
```

### Option 2: Using uvicorn directly
```bash
# Start with auto-reload
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Or with more specific reload options
uvicorn main:app --host 0.0.0.0 --port 8000 --reload --reload-dir . --reload-exclude "*.json"
```

### Option 3: Using npm scripts (if you have Node.js installed)
```bash
# Install dependencies first
npm run install-deps

# Start development server
npm run dev

# Or use the reload script
npm run dev:reload
```

### Option 4: Windows Batch Script
```cmd
# Double-click or run from command line
start_dev.bat
```

### Option 5: PowerShell Script
```powershell
# Run PowerShell script
.\start_dev.ps1
```

## 🔄 Auto-Reload Features

### What Gets Watched:
- All `.py` files in the current directory and subdirectories
- Changes to imported modules
- Configuration files

### What Gets Excluded:
- `*.pyc` files (compiled Python files)
- `__pycache__` directories
- `*.log` files
- `*.json` files (data files)
- `*.csv` files
- `*.xlsx` files
- `static/*` (frontend files)
- `node_modules/*` (if any)

### How It Works:
1. **File Monitoring**: The server watches for file changes in real-time
2. **Automatic Restart**: When a Python file is modified, the server automatically restarts
3. **Hot Reload**: The application reloads without manual intervention
4. **Error Handling**: If there's a syntax error, the server will show the error and wait for fixes

## 📁 File Structure for Auto-Reload

```
StockWebApi/
├── main.py              # Main FastAPI application
├── dev_server.py        # Development server script
├── start_dev.bat        # Windows batch script
├── start_dev.ps1        # PowerShell script
├── package.json         # NPM scripts
├── requirements.txt     # Python dependencies
├── enhanced_stock_operations.py
├── stock_operations.py
├── auth_operations.py
├── models.py
└── ... (other Python files)
```

## 🛠️ Development Workflow

1. **Start the server** with one of the methods above
2. **Make changes** to any Python file
3. **Save the file** - the server will automatically reload
4. **Test your changes** - no need to restart manually
5. **View logs** in the terminal for any errors

## 🔧 Configuration Options

### Custom Reload Directories
```python
# In dev_server.py, modify reload_dirs:
"reload_dirs": [".", "..", "../shared"],  # Add more directories to watch
```

### Custom Exclusions
```python
# In dev_server.py, modify reload_excludes:
"reload_excludes": [
    "*.pyc", 
    "__pycache__", 
    "*.log", 
    "*.json",
    "data/*",  # Exclude data directory
    "logs/*"   # Exclude logs directory
],
```

### Environment Variables
```bash
# Set environment variables for development
export PYTHONPATH=.
export ENVIRONMENT=development
export DEBUG=True
```

## 🐛 Troubleshooting

### Server Not Reloading
1. Check if the file is in the watched directory
2. Ensure the file has a `.py` extension
3. Check if the file is in the exclusion list
4. Restart the development server

### Import Errors After Reload
1. Check for syntax errors in modified files
2. Ensure all imports are correct
3. Check the terminal for error messages
4. Restart the server if needed

### Performance Issues
1. Reduce the number of watched directories
2. Add more files to exclusion list
3. Use `--reload-exclude` to exclude large files
4. Consider using `--workers 1` for development

## 📝 Best Practices

1. **Use the development server** for all development work
2. **Keep the terminal open** to see reload messages and errors
3. **Test frequently** - the auto-reload makes it easy to iterate quickly
4. **Check logs** for any issues during development
5. **Use version control** to track changes

## 🚀 Production Deployment

For production, use the regular server without auto-reload:
```bash
# Production server (no auto-reload)
python main.py

# Or with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [Python Development Best Practices](https://docs.python.org/3/tutorial/)
