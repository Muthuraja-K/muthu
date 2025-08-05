# Stock Prediction API

A FastAPI-based stock prediction and analysis application with parallel processing capabilities.

## Features

- **FastAPI Framework**: Modern, fast web framework with automatic API documentation
- **Parallel Processing**: Optimized stock data fetching with concurrent processing
- **JWT Authentication**: Secure token-based authentication
- **Stock Analysis**: Real-time stock data, historical analysis, and sentiment analysis
- **Sector Management**: Group stocks by sectors with performance tracking
- **User Management**: Role-based access control (Admin/User)

## Railway Deployment

### Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Git Repository**: Your code should be in a Git repository (GitHub, GitLab, etc.)

### Deployment Steps

#### Method 1: Deploy from GitHub (Recommended)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Ready for Railway deployment"
   git push origin main
   ```

2. **Deploy on Railway**:
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will automatically detect it's a Python project

3. **Configure Environment Variables** (if needed):
   - Go to your project settings
   - Add any environment variables under "Variables" tab

#### Method 2: Deploy from Local Directory

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Deploy**:
   ```bash
   railway init
   railway up
   ```

### Configuration Files

The following files are configured for Railway deployment:

- **`railway.toml`**: Railway-specific configuration
- **`Procfile.txt`**: Process definition for Railway
- **`requirements.txt`**: Python dependencies
- **`.gitignore`**: Excludes unnecessary files

### User Configuration

The application uses existing user information from `user.json`. No default users are created on startup since user data is already configured.

### API Documentation

Once deployed, you can access:
- **API Documentation**: `https://your-app.railway.app/docs`
- **Alternative Docs**: `https://your-app.railway.app/redoc`

### Environment Variables

You can set these in Railway dashboard:

- `PYTHON_VERSION`: Python version (default: 3.11)
- `PORT`: Port number (auto-set by Railway)

### Performance Features

- **Parallel Processing**: Stock data fetching uses ThreadPoolExecutor
- **Multiple Workers**: Gunicorn with 4 workers for better performance
- **CORS Enabled**: Frontend can communicate with the API
- **Static File Serving**: Angular frontend files served automatically

### Monitoring

- Check Railway dashboard for logs and performance metrics
- Application logs are available in Railway console
- Monitor resource usage in Railway dashboard

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python main.py
# or
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Authentication
- `POST /api/login` - User login
- `POST /api/verify-token` - Verify JWT token

### Stock Data
- `GET /api/getstock` - Get stock list (requires auth)
- `GET /api/getstockdetails` - Get detailed stock info (requires auth)
- `GET /api/stock-summary` - Get sector-based stock summary (requires auth)

### Admin Only
- `POST /api/stocks` - Add stock
- `PUT /api/stocks/update` - Update stock
- `POST /api/stocks/delete` - Delete stock
- `GET /api/sectors` - Get sectors
- `GET /api/users` - Get users

## Support

For deployment issues, check:
1. Railway logs in the dashboard
2. Application logs in the console
3. Environment variables configuration
4. Network connectivity and firewall settings 