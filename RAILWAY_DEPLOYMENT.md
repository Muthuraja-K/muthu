# Railway Deployment Guide

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Git Repository**: Your code should be in a Git repository (GitHub, GitLab, etc.)

## Deployment Steps

### 1. Connect to Railway

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Choose "Deploy from GitHub repo" (or your preferred Git provider)
4. Select your repository

### 2. Configure Environment Variables (Optional)

Railway will automatically detect the Python application. You can add environment variables in the Railway dashboard:

- `PYTHON_VERSION`: 3.11.7 (already set in runtime.txt)
- `PORT`: Automatically set by Railway
- Any other environment variables your app needs

### 3. Deploy

1. Railway will automatically build and deploy your application
2. The build process will:
   - Install Python 3.11.7
   - Install dependencies from `requirements.txt`
   - Start the application using the command in `Procfile`

### 4. Monitor Deployment

- Check the deployment logs in Railway dashboard
- Monitor the health check endpoint: `https://your-app.railway.app/health`
- View application logs for any issues

## Configuration Files

### `railway.toml`
- Configures the build and deployment process
- Sets health check endpoint and restart policies
- Specifies Python version

### `Procfile`
- Tells Railway how to start the application
- Uses Gunicorn with Uvicorn workers for production

### `requirements.txt`
- Lists all Python dependencies with specific versions
- Ensures consistent builds

### `runtime.txt`
- Specifies Python version (3.11.7)

### `.dockerignore`
- Excludes unnecessary files from the build
- Reduces build time and image size

## Health Check

The application includes a health check endpoint at `/health` that returns:
```json
{
  "status": "healthy",
  "message": "Stock Prediction API is running"
}
```

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check `requirements.txt` for correct dependencies
   - Ensure all imports are available
   - Check Railway build logs

2. **Runtime Errors**
   - Check application logs in Railway dashboard
   - Verify environment variables are set correctly
   - Ensure data files (JSON) are present

3. **Health Check Failures**
   - Verify the `/health` endpoint is accessible
   - Check if the application is starting correctly
   - Review startup logs

### Logs

- **Build Logs**: Available during deployment
- **Application Logs**: Available in Railway dashboard
- **Health Check Logs**: Available in Railway monitoring

## Performance Optimization

- **Workers**: Set to 2 for Railway's free tier
- **Timeout**: 120 seconds for long-running requests
- **Memory**: Monitor usage in Railway dashboard
- **CPU**: Optimize for Railway's resource limits

## Scaling

- **Free Tier**: 1 instance, limited resources
- **Pro Tier**: Multiple instances, more resources
- **Custom**: Configure based on your needs

## Security

- **Environment Variables**: Store sensitive data in Railway environment variables
- **HTTPS**: Automatically provided by Railway
- **CORS**: Configure appropriately for your frontend domain
- **Authentication**: Ensure JWT tokens are properly configured

## Maintenance

- **Updates**: Push to your Git repository to trigger automatic deployments
- **Monitoring**: Use Railway's built-in monitoring tools
- **Backups**: Ensure your data files are backed up
- **Logs**: Regularly check application logs for issues
