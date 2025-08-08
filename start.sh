#!/bin/bash

# Debug information
echo "Starting Stock Prediction API..."
echo "Python version: $(python --version)"
echo "Current directory: $(pwd)"
echo "Files in current directory:"
ls -la

# Check if gunicorn is installed
echo "Checking gunicorn installation..."
python -c "import gunicorn; print('Gunicorn version:', gunicorn.__version__)"

# Check if uvicorn is installed
echo "Checking uvicorn installation..."
python -c "import uvicorn; print('Uvicorn version:', uvicorn.__version__)"

# Check if main.py exists
if [ -f "main.py" ]; then
    echo "main.py found"
else
    echo "ERROR: main.py not found!"
    exit 1
fi

# Start the application
echo "Starting application with gunicorn..."
exec gunicorn main:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120
