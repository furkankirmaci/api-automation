#!/usr/bin/env python3
"""
Test API Server - Mock server for testing API automation tool
Provides 10 different endpoints covering various scenarios
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import uuid
import time
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)

# In-memory storage for testing
users_db = []
products_db = []
auth_tokens = {}

# Sample data
sample_users = [
    {"id": 1, "name": "John Doe", "email": "john@example.com", "role": "admin", "active": True},
    {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "role": "user", "active": True},
    {"id": 3, "name": "Bob Johnson", "email": "bob@example.com", "role": "user", "active": False}
]

sample_products = [
    {"id": 1, "name": "Laptop", "description": "High-performance laptop", "price": 999.99, "category": "electronics", "stock": 50},
    {"id": 2, "name": "Smartphone", "description": "Latest smartphone model", "price": 699.99, "category": "electronics", "stock": 100},
    {"id": 3, "name": "Book", "description": "Programming guide", "price": 29.99, "category": "books", "stock": 200}
]

# Initialize with sample data
users_db.extend(sample_users)
products_db.extend(sample_products)

def generate_token():
    """Generate a simple auth token"""
    return str(uuid.uuid4())

def verify_token():
    """Verify authentication token"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    return token if token in auth_tokens else None

def require_auth(f):
    """Decorator to require authentication"""
    def decorated_function(*args, **kwargs):
        if not verify_token():
            return jsonify({"error": "Unauthorized", "message": "Valid token required"}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": "running",
        "version": "1.0.0"
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # Simple validation
        if username == 'admin' and password == 'password123':
            token = generate_token()
            auth_tokens[token] = {
                'user_id': 1,
                'username': username,
                'expires': time.time() + 3600  # 1 hour
            }
            
            return jsonify({
                "success": True,
                "message": "Login successful",
                "token": token,
                "user": {
                    "id": 1,
                    "username": username,
                    "role": "admin"
                }
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Invalid credentials"
            }), 401
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Login failed",
            "error": str(e)
        }), 400

@app.route('/api/auth/logout', methods=['POST'])
@require_auth
def logout():
    """User logout endpoint"""
    token = verify_token()
    if token in auth_tokens:
        del auth_tokens[token]
    
    return jsonify({
        "success": True,
        "message": "Logout successful"
    })

@app.route('/api/users', methods=['GET'])
@require_auth
def get_users():
    """Get all users with pagination"""
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    
    paginated_users = users_db[start_idx:end_idx]
    
    return jsonify({
        "users": paginated_users,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": len(users_db),
            "pages": (len(users_db) + limit - 1) // limit
        }
    })

@app.route('/api/users', methods=['POST'])
@require_auth
def create_user():
    """Create a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'role']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "message": f"Missing required field: {field}"
                }), 400
        
        # Check if email already exists
        if any(user['email'] == data['email'] for user in users_db):
            return jsonify({
                "success": False,
                "message": "Email already exists"
            }), 409
        
        # Create new user
        new_user = {
            "id": max([u['id'] for u in users_db], default=0) + 1,
            "name": data['name'],
            "email": data['email'],
            "role": data['role'],
            "active": data.get('active', True)
        }
        
        users_db.append(new_user)
        
        return jsonify({
            "success": True,
            "message": "User created successfully",
            "user": new_user
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Failed to create user",
            "error": str(e)
        }), 400

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@require_auth
def update_user(user_id):
    """Update an existing user"""
    try:
        data = request.get_json()
        
        # Find user
        user = next((u for u in users_db if u['id'] == user_id), None)
        if not user:
            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404
        
        # Update user
        user.update({
            "name": data.get('name', user['name']),
            "email": data.get('email', user['email']),
            "role": data.get('role', user['role']),
            "active": data.get('active', user['active'])
        })
        
        return jsonify({
            "success": True,
            "message": "User updated successfully",
            "user": user
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Failed to update user",
            "error": str(e)
        }), 400

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@require_auth
def delete_user(user_id):
    """Delete a user"""
    global users_db
    
    # Find user
    user = next((u for u in users_db if u['id'] == user_id), None)
    if not user:
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404
    
    # Remove user
    users_db = [u for u in users_db if u['id'] != user_id]
    
    return jsonify({
        "success": True,
        "message": "User deleted successfully"
    })

@app.route('/api/products', methods=['GET'])
@require_auth
def get_products():
    """Get products with filtering"""
    category = request.args.get('category')
    sort = request.args.get('sort', 'id')
    
    filtered_products = products_db.copy()
    
    # Filter by category
    if category:
        filtered_products = [p for p in filtered_products if p['category'] == category]
    
    # Sort products
    if sort == 'price':
        filtered_products.sort(key=lambda x: x['price'])
    elif sort == 'name':
        filtered_products.sort(key=lambda x: x['name'])
    
    return jsonify({
        "products": filtered_products,
        "filters": {
            "category": category,
            "sort": sort
        },
        "total": len(filtered_products)
    })

@app.route('/api/products', methods=['POST'])
@require_auth
def create_product():
    """Create a new product"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'description', 'price', 'category']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "message": f"Missing required field: {field}"
                }), 400
        
        # Create new product
        new_product = {
            "id": max([p['id'] for p in products_db], default=0) + 1,
            "name": data['name'],
            "description": data['description'],
            "price": float(data['price']),
            "category": data['category'],
            "stock": data.get('stock', 0)
        }
        
        products_db.append(new_product)
        
        return jsonify({
            "success": True,
            "message": "Product created successfully",
            "product": new_product
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Failed to create product",
            "error": str(e)
        }), 400

@app.route('/api/system/info', methods=['GET'])
@require_auth
def get_system_info():
    """Get system information"""
    return jsonify({
        "system": {
            "name": "Test API Server",
            "version": "1.0.0",
            "environment": "development"
        },
        "statistics": {
            "total_users": len(users_db),
            "total_products": len(products_db),
            "active_tokens": len(auth_tokens)
        },
        "timestamp": datetime.now().isoformat()
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Not Found",
        "message": "The requested resource was not found"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal Server Error",
        "message": "An unexpected error occurred"
    }), 500

if __name__ == '__main__':
    print("🚀 Starting Test API Server...")
    print("📋 Available endpoints:")
    print("   GET  /api/health - Health check")
    print("   POST /api/auth/login - User login")
    print("   POST /api/auth/logout - User logout")
    print("   GET  /api/users - Get all users")
    print("   POST /api/users - Create user")
    print("   PUT  /api/users/{id} - Update user")
    print("   DELETE /api/users/{id} - Delete user")
    print("   GET  /api/products - Get products")
    print("   POST /api/products - Create product")
    print("   GET  /api/system/info - System info")
    print("\n🔐 Test credentials:")
    print("   Username: admin")
    print("   Password: password123")
    print("\n🌐 Server will start at: http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
