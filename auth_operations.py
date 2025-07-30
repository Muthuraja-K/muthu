import json
import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify

# Secret key for JWT tokens (in production, use a secure secret key)
SECRET_KEY = "your-secret-key-here-change-in-production"

def load_users():
    """Load users from user.json file"""
    try:
        with open('user.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_users(users):
    """Save users to user.json file"""
    with open('user.json', 'w') as file:
        json.dump(users, file, indent=2)

def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed_password):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_token(username, role, firstname, lastname):
    """Create a JWT token for the user"""
    payload = {
        'username': username,
        'role': role,
        'firstname': firstname,
        'lastname': lastname,
        'exp': datetime.utcnow() + timedelta(hours=24)  # Token expires in 24 hours
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def login_user(username, password):
    """Authenticate a user and return token if successful"""
    users = load_users()
    
    for user in users:
        if user['username'] == username and verify_password(password, user['password']):
            firstname = user.get('firstname', '')
            lastname = user.get('lastname', '')
            token = create_token(username, user['role'], firstname, lastname)
            return {
                'success': True,
                'token': token,
                'username': username,
                'role': user['role'],
                'firstname': firstname,
                'lastname': lastname
            }
    
    return {
        'success': False,
        'message': 'Invalid username or password'
    }

def require_auth(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Add user info to request
        request.user = payload
        return f(*args, **kwargs)
    
    return decorated_function

def require_admin(f):
    """Decorator to require admin role for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        if payload.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Add user info to request
        request.user = payload
        return f(*args, **kwargs)
    
    return decorated_function

def create_default_users():
    """Create default users if user.json doesn't exist"""
    if not os.path.exists('user.json'):
        default_users = [
            {
                "username": "admin",
                "password": hash_password("admin123"),
                "role": "admin",
                "firstname": "Admin",
                "lastname": "User"
            },
            {
                "username": "user",
                "password": hash_password("user123"),
                "role": "user",
                "firstname": "Regular",
                "lastname": "User"
            }
        ]
        save_users(default_users)
        print("Default users created:")
        print("Admin - username: admin, password: admin123")
        print("User - username: user, password: user123") 