import bcrypt
import json

def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Create default users with properly hashed passwords
default_users = [
    {
        "username": "admin",
        "password": hash_password("Stock@Friends"),
        "role": "admin",
        "firstname": "Admin",
        "lastname": "User"
    },
    {
        "username": "user",
        "password": hash_password("Stock@2026"),
        "role": "user",
        "firstname": "Regular",
        "lastname": "User"
    }
]

# Save to user.json
with open('user.json', 'w') as file:
    json.dump(default_users, file, indent=2)

print("Default users created:")
print("Admin - username: admin, password: Stock@Friends")
print("User - username: user, password: Stock@2026")
print("User.json file has been created with properly hashed passwords.") 