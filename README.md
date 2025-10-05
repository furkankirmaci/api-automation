# 🚀 API Test Automation Tool

A powerful, zero-config GUI application for testing APIs from Postman collections. Import any collection, run individual requests, or automate entire test suites with dynamic data and automatic authentication handling.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## ✨ Features

- **📥 Import Any Collection**: Works with any Postman collection JSON
- **🔐 Smart Authentication**: Automatic Bearer token and XSRF token handling
- **🤖 Test Automation**: Queue and run multiple API calls sequentially
- **🎯 Dynamic Templates**: Edit request data and save custom templates
- **📊 Detailed Logging**: Complete request/response details with timing
- **💾 Export Results**: Save logs and copy to clipboard
- **🎨 Modern UI**: Clean, intuitive interface with emoji indicators

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Windows, macOS, or Linux

### Installation
```bash
# Clone the repository
git clone https://github.com/furkankirmaci/api-automation.git
cd api-automation

# Install dependencies
pip install -r requirements.txt

# Run the application
python api_automation_tool.py
```

### Test with Sample Collection
```bash
# Start the included test server
python Test_API_Server.py

# Import Test_API_Collection.json in the tool
# Login with: admin / password123
# Run automation to see it in action!
```

## 📖 Usage

### 1. Import Collection
- Click **"Import"** → Select your Postman collection JSON
- Choose categories to import
- All endpoints are automatically parsed and organized

### 2. Test Individual APIs
- Select a category and method
- Click **"Load Template"** to populate the request builder
- Edit headers, body, or parameters as needed
- Click **"Send Request"** to test

### 3. Run Automation
- Add methods to the automation queue using **"Add"**
- Reorder with **↑/↓** buttons
- Click **"Run Automation"** to execute all queued requests
- View results with ✅/❌ status indicators

## 🔐 Authentication Features

### Automatic Token Management
- **Bearer Tokens**: Extracted from login responses and auto-added to requests
- **XSRF Tokens**: Captured from headers, cookies, or Set-Cookie
- **Variable Replacement**: `{{authToken}}` and `{{xsrf_token}}` automatically replaced
- **Session Persistence**: Tokens maintained across all requests

### Supported Auth Types
- Bearer Token authentication
- XSRF/CSRF token protection
- Custom header authentication
- Cookie-based sessions

## 🛠️ Advanced Features

### Dynamic Templates
- Edit request data and save as custom templates
- Different data for each method in automation
- Preserve original templates while using modified versions

### Smart Field Visibility
- **GET**: Shows only query parameters
- **POST/PUT**: Shows only request body
- **DELETE**: Shows both body and parameters
- **Headers**: Always visible for all methods

### Collection Variables
- Automatic `{{baseUrl}}` replacement from collection variables
- Support for all Postman variable types
- Clean URL construction and validation

## 📁 Project Structure

```
api-automation-tool/
├── api_automation_tool.py      # Main application
├── Test_API_Server.py          # Sample test server
├── Test_API_Collection.json    # Sample Postman collection
├── requirements.txt            # Python dependencies
├── README.md                   # User documentation
└── QUICK_START.md             # Quick start guide
```

## 🧪 Testing

The project includes a complete test environment:

### Test Server (`Test_API_Server.py`)
- Flask-based mock server with 10 realistic endpoints
- Authentication system with Bearer tokens
- CRUD operations for users and products
- Health check and system info endpoints

### Test Collection (`Test_API_Collection.json`)
- 4 categories: Authentication, User Management, Product Management, System
- 10 endpoints covering various HTTP methods
- Realistic request/response examples
- Proper authentication flow

## 🔧 Configuration

### Environment Variables
- No configuration required - works out of the box
- SSL verification disabled for development convenience
- 30-second timeout for all requests

### Customization
- Modify `Test_API_Collection.json` for different endpoints
- Edit `Test_API_Server.py` for custom server behavior
- Extend authentication logic in the main application

## 🤝 Contributing

Contributions are welcome! Here are some areas where help is needed:

- **Parser Improvements**: Support for more Postman collection formats
- **Authentication**: Additional auth flows (OAuth2, JWT helpers)
- **Export Formats**: Better report generation (HTML, PDF, Excel)
- **UI Enhancements**: Dark mode, themes, better mobile support
- **Testing**: More comprehensive test coverage

### Development Setup
```bash
# Fork the repository
git clone https://github.com/furkankirmaci/api-automation.git
cd api-automation

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Start development server
python Test_API_Server.py
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with Python, Tkinter, and Requests
- Inspired by Postman's collection format
- Thanks to the Flask community for the test server framework

---

**Made with ❤️ for the API testing community**

*Star this repository if you find it helpful!*
