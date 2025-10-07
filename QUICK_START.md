# Quick Start Guide - Test API Collection

## 🚀 Get Started in 3 Steps

### 1. Start the Test Server
```bash
# Install additional dependencies for the test server
pip install flask flask-cors

# Start the test API server
python Test_API_Server.py
```
The server will start at `http://localhost:5000`

### 2. Import the Collection
1. Open the API Test Automation Tool
2. Click **"Import"** button
3. Select `Test_API_Collection.json`
4. Choose all categories (Authentication, User Management, Product Management, System)

### 3. Test the APIs
1. **Login First**: Select "Authentication" → "Login" → Load Template → Send Request
2. **Token Auto-Extraction**: The tool automatically extracts and stores the Bearer token
3. **Test Protected Endpoints**: Select any other method → Load Template → Send Request
4. **Automation**: Add methods to automation list and run them sequentially

## 📋 Available Test Endpoints

### Authentication (2 endpoints)
- **POST /api/auth/login** - Login with admin/password123
- **POST /api/auth/logout** - Logout (requires token)

### User Management (4 endpoints)  
- **GET /api/users** - Get all users (with pagination)
- **POST /api/users** - Create new user
- **PUT /api/users/{id}** - Update user
- **DELETE /api/users/{id}** - Delete user

### Product Management (2 endpoints)
- **GET /api/products** - Get products (with filtering)
- **POST /api/products** - Create new product

### System (2 endpoints)
- **GET /api/health** - Health check (no auth required)
- **GET /api/system/info** - System information

## 🔐 Test Credentials
- **Username**: `admin`
- **Password**: `password123`

## 🎯 Automation Example
1. **Login First**: Add "Authentication" → "Login" to automation list
2. **Add Protected Endpoints**: Add "User Management" → "Get All Users" to automation list  
3. **Add More Methods**: Add "Product Management" → "Get Products" to automation list
4. **Run Automation**: Click "Run Automation" - tokens are automatically managed

## 💡 Tips
- **Automatic Authentication**: Bearer tokens are extracted from login and added to all subsequent requests
- **No Manual Token Management**: The tool handles authentication automatically
- **Sample Data**: Test server includes 3 users and 3 products pre-loaded
- **Realistic Responses**: All endpoints return proper JSON with status codes
- **Query Parameters**: Use URL-encoded format (page=1&limit=10) in the Query Parameters field
- **Token Expiry**: Authentication tokens expire after 1 hour
- **Port Configuration**: Server runs on port 5000 (modify if needed)

## 🛠️ Customization
Edit `Test_API_Collection.json` to:
- Change base URL
- Modify request bodies
- Add more endpoints
- Update variables

Edit `Test_API_Server.py` to:
- Add new endpoints
- Modify response formats
- Change authentication logic
- Add more sample data
