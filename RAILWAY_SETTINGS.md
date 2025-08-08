# Railway Settings Configuration Guide

## Environment Variables

### Required Environment Variables

1. **SECRET_KEY** (Required for JWT Authentication)
   - **Description**: Secret key for JWT token generation and verification
   - **Default**: `"your-production-secret-key-change-this-in-railway-dashboard"`
   - **Production**: Generate a secure random key (32+ characters)
   - **How to set**: In Railway dashboard → Environment Variables

2. **ALLOWED_ORIGINS** (Optional)
   - **Description**: Comma-separated list of allowed CORS origins
   - **Default**: `"*"` (allows all origins)
   - **Production**: Set to your frontend domain(s)
   - **Example**: `"https://your-app.railway.app,https://yourdomain.com"`

3. **PORT** (Auto-set by Railway)
   - **Description**: Port number for the application
   - **Default**: `8000`
   - **Note**: Automatically set by Railway, don't change

4. **PYTHON_VERSION** (Auto-set by runtime.txt)
   - **Description**: Python version for the application
   - **Default**: `3.11.7`
   - **Note**: Set in runtime.txt, don't change

### Optional Environment Variables

5. **LOG_LEVEL** (Optional)
   - **Description**: Logging level for the application
   - **Default**: `INFO`
   - **Options**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

## Railway Dashboard Configuration

### 1. Environment Variables Setup

1. Go to your Railway project dashboard
2. Click on your service
3. Go to "Variables" tab
4. Add the following variables:

```
SECRET_KEY=your-secure-production-secret-key-here
ALLOWED_ORIGINS=https://your-app.railway.app,https://yourdomain.com
LOG_LEVEL=INFO
```

### 2. Domain Configuration

1. Go to "Settings" tab
2. Under "Domains", you can:
   - Use the default Railway domain
   - Add a custom domain (if you have one)

### 3. Health Check Configuration

- **Health Check Path**: `/health`
- **Health Check Timeout**: 300 seconds
- **Restart Policy**: On failure
- **Max Retries**: 3

## Security Considerations

### 1. SECRET_KEY Security

**⚠️ IMPORTANT**: Change the default SECRET_KEY in production!

```bash
# Generate a secure secret key (run this locally)
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. CORS Configuration

For production, restrict CORS to your actual domains:

```
ALLOWED_ORIGINS=https://your-app.railway.app,https://yourdomain.com
```

### 3. Environment Variable Best Practices

- Never commit sensitive values to version control
- Use Railway's environment variable feature
- Rotate secrets regularly
- Use different secrets for different environments

## Monitoring and Logs

### 1. Application Logs

- View logs in Railway dashboard → "Deployments" tab
- Logs are automatically captured and displayed
- Use `LOG_LEVEL=DEBUG` for detailed debugging

### 2. Health Monitoring

- Health check endpoint: `https://your-app.railway.app/health`
- Returns: `{"status": "healthy", "message": "Stock Prediction API is running"}`
- Railway automatically monitors this endpoint

### 3. Performance Monitoring

- Railway provides built-in performance metrics
- Monitor CPU, memory, and network usage
- Set up alerts for resource limits

## Troubleshooting

### Common Issues

1. **Application not starting**
   - Check logs in Railway dashboard
   - Verify all environment variables are set
   - Ensure `requirements.txt` is up to date

2. **CORS errors**
   - Verify `ALLOWED_ORIGINS` is set correctly
   - Check if frontend domain is included

3. **Authentication issues**
   - Verify `SECRET_KEY` is set and secure
   - Check JWT token expiration

4. **Static files not loading**
   - Ensure `static/` directory exists
   - Check if `index.html` is present

### Debug Commands

```bash
# Test application locally
python test_startup.py

# Check environment variables
echo $SECRET_KEY
echo $ALLOWED_ORIGINS

# Test health endpoint
curl https://your-app.railway.app/health
```

## Deployment Checklist

- [ ] Environment variables configured
- [ ] SECRET_KEY changed from default
- [ ] CORS origins configured
- [ ] Health check endpoint working
- [ ] Static files accessible
- [ ] Authentication working
- [ ] Logs being captured
- [ ] Performance monitoring enabled

## Support

For Railway-specific issues:
- Check Railway documentation: https://docs.railway.app/
- Contact Railway support through dashboard
- Check Railway status page: https://status.railway.app/
