import requests
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
from typing import Dict, Optional, Tuple
import urllib3
import webbrowser
from datetime import datetime

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class APITestAutomationTool:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 API Test Automation Tool")
        self.root.geometry("1600x950")
        self.root.configure(bg='#1e1e2e')  # Dark theme background
        
        # Define color scheme
        self.colors = {
            'bg_primary': '#1e1e2e',      # Dark blue-gray
            'bg_secondary': '#2d2d44',    # Lighter blue-gray
            'bg_accent': '#3b3b5c',       # Accent blue-gray
            'text_primary': '#ffffff',    # White text
            'text_secondary': '#b8b8d1',  # Light gray text
            'accent_blue': '#4a9eff',     # Bright blue
            'accent_green': '#4ade80',    # Bright green
            'accent_orange': '#fb923c',   # Bright orange
            'accent_purple': '#a78bfa',   # Bright purple
            'accent_red': '#f87171',      # Bright red
            'success': '#10b981',         # Success green
            'warning': '#f59e0b',         # Warning orange
            'error': '#ef4444'            # Error red
        }
        
        # Login methods storage
        
        # Optimized dimensions for 15.6 inch laptop
        self.root.minsize(1200, 700)
        
        # Fill screen completely - better sizing
        self.root.state('zoomed')  # For Windows
        
        # Add padding for full screen bottom visibility
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Leave space for taskbar (approximately 40px)
        available_height = screen_height - 40
        self.root.geometry(f"{screen_width}x{available_height}")
        
        
        
        self.session = requests.Session()
        self.session.verify = False
        self.base_url = ""
        self.xsrf_token = ""
        self.auth_token = ""  # For Bearer token authentication
        self.session_id = ""
        self.selected_category = ""
        self.selected_method = ""
        
        # Dynamic template storage - store current templates for each method
        self.dynamic_templates = {}
        
        # Separate storage for saved fields
        self.saved_headers = {}
        self.saved_bodies = {}
        self.saved_params = {}
        self.saved_urls = {}
        self.saved_paths = {}
        
        # For API collection import
        self.imported_apis = {}
        self.category_structure = {}
        self.expanded_categories = set()  # Track which categories are expanded
        self.collection_loaded = False
        self.collection_variables = {}  # Store collection variables like baseUrl
        
        # No hardcoded APIs - collection must be imported first
        self.sample_apis = {}
        
        self.create_widgets()
    
    
    def create_widgets(self):
        # Create main frame - modern theme
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(1, weight=1)
        
        self.create_single_screen(main_frame)
    
    def create_single_screen(self, main_frame):
        # Left panel - Login and API selection (flexible size)
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Orta panel - Request Builder
        middle_frame = ttk.Frame(main_frame)
        middle_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Right panel - Results
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Grid weights - flexible sizing (optimized for full screen)
        main_frame.columnconfigure(0, weight=2)  # Sol panel (daha dar)
        main_frame.columnconfigure(1, weight=3)  # Middle panel (wider)
        main_frame.columnconfigure(2, weight=3)  # Right panel (wider - for logs)
        
        # Left panel content
        self.create_left_panel(left_frame)
        
        # Middle panel content
        self.create_middle_panel(middle_frame)
        
        # Right panel content
        self.create_right_panel(right_frame)
    
    def create_left_panel(self, parent):
        # Import Collection section (at the top)
        import_frame = ttk.LabelFrame(parent, text="📥 Import Collection", padding="10")
        import_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Import Collection buttons
        import_button_frame = ttk.Frame(import_frame)
        import_button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        
        self.import_collection_button = ttk.Button(import_button_frame, text="📥 Import", command=self.import_api_collection)
        self.import_collection_button.grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.export_collection_button = ttk.Button(import_button_frame, text="📤 Export", command=self.export_api_collection, state=tk.DISABLED)
        self.export_collection_button.grid(row=0, column=1, sticky=tk.W, padx=(0, 5))
        
        self.remove_collection_button = ttk.Button(import_button_frame, text="🗑 Remove", command=self.remove_collection, state=tk.NORMAL)
        self.remove_collection_button.grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        
        # Import status label
        self.import_status_label = ttk.Label(import_frame, text="No collection imported", foreground="gray")
        self.import_status_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # API selection section (compact)
        api_frame = ttk.LabelFrame(parent, text="🎯 API Selection", padding="10")
        api_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # API categories (flexible size)
        ttk.Label(api_frame, text="Category:").grid(row=0, column=0, sticky=tk.W, pady=2)
        
        # Category listbox with scrollbar
        category_frame = ttk.Frame(api_frame)
        category_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        self.category_listbox = tk.Listbox(category_frame, height=8, width=35)
        self.category_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        category_scrollbar = ttk.Scrollbar(category_frame, orient=tk.VERTICAL, command=self.category_listbox.yview)
        category_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.category_listbox.config(yscrollcommand=category_scrollbar.set)
        
        self.category_listbox.bind('<<ListboxSelect>>', self.on_category_select)
        
        # Categories will be populated when collection is imported
        self.category_listbox.insert(tk.END, "⚠️ No collection imported")
        
        # API methods (flexible size)
        ttk.Label(api_frame, text="Method:").grid(row=2, column=0, sticky=tk.W, pady=(10, 2))
        self.method_listbox = tk.Listbox(api_frame, height=8, width=35)
        self.method_listbox.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        self.method_listbox.bind('<<ListboxSelect>>', self.on_method_select)
        
        # Test buttons
        # Load Template Button
        self.load_template_button = ttk.Button(api_frame, text="Load Template", command=self.load_template, state=tk.NORMAL)
        self.load_template_button.grid(row=4, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        # Automation section - Modern style (compact)
        automation_frame = ttk.LabelFrame(parent, text="🤖 Automation", padding="10")
        automation_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        
        # Method sorting (flexible size)
        ttk.Label(automation_frame, text="Method Order:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.method_order_listbox = tk.Listbox(automation_frame, height=6, width=35)
        self.method_order_listbox.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        # Sorting buttons
        order_button_frame = ttk.Frame(automation_frame)
        order_button_frame.grid(row=2, column=0, columnspan=2, pady=5)
        
        ttk.Button(order_button_frame, text="↑", command=self.move_method_up, width=3).grid(row=0, column=0, padx=1)
        ttk.Button(order_button_frame, text="↓", command=self.move_method_down, width=3).grid(row=0, column=1, padx=1)
        ttk.Button(order_button_frame, text="Remove", command=self.remove_from_order, width=8).grid(row=0, column=2, padx=1)
        ttk.Button(order_button_frame, text="Add", command=self.add_to_order, width=8).grid(row=0, column=3, padx=1)
        
        # Automation buttons
        automation_button_frame = ttk.Frame(automation_frame)
        automation_button_frame.grid(row=3, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        self.run_automation_button = ttk.Button(automation_button_frame, text="Run Automation", command=self.run_automation, state=tk.NORMAL)
        self.run_automation_button.grid(row=0, column=0, padx=2)
        
        self.stop_automation_button = ttk.Button(automation_button_frame, text="Stop", command=self.stop_automation, state=tk.NORMAL)
        self.stop_automation_button.grid(row=0, column=1, padx=2)
        
        # Otomasyon durumu
        self.automation_status_label = ttk.Label(automation_frame, text="Ready", foreground="blue")
        self.automation_status_label.grid(row=4, column=0, columnspan=2, pady=2, sticky=(tk.W, tk.E))
        
        # Automation variables
        self.automation_running = False
        self.automation_methods = []
        self._automation_queue = []  # Copy to be consumed during active execution
        self.automation_results = {}  # To store method results
        
        # Grid weights
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)  # Import frame
        parent.rowconfigure(1, weight=1)  # API frame (less space)
        parent.rowconfigure(2, weight=4)  # Automation frame (en fazla alan)
        api_frame.columnconfigure(0, weight=1)
        automation_frame.columnconfigure(0, weight=1)
    
    def create_middle_panel(self, parent):
        # Request Builder section - Modern style (compact)
        builder_frame = ttk.LabelFrame(parent, text="🛠️ Request Builder", padding="10")
        builder_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Method, URL ve Path
        ttk.Label(builder_frame, text="Method:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.method_combo = ttk.Combobox(builder_frame, values=["GET", "POST", "PUT", "DELETE"], width=8)
        self.method_combo.grid(row=0, column=1, sticky=tk.W, pady=2)
        self.method_combo.set("GET")
        
        ttk.Label(builder_frame, text="URL:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.base_url_entry = ttk.Entry(builder_frame, width=50)
        self.base_url_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        # Don't insert default value - will be populated from collection
        
        # Base URL Save Button
        self.save_url_button = ttk.Button(builder_frame, text="💾 Save URL", command=self.save_url, state=tk.NORMAL)
        self.save_url_button.grid(row=2, column=0, sticky=tk.W, pady=2)
        
        ttk.Label(builder_frame, text="Path:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.path_entry = ttk.Entry(builder_frame, width=50)
        self.path_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Path Save Button
        self.save_path_button = ttk.Button(builder_frame, text="💾 Save Path", command=self.save_path, state=tk.NORMAL)
        self.save_path_button.grid(row=4, column=0, sticky=tk.W, pady=2)
        
        # Headers
        ttk.Label(builder_frame, text="Headers:", font=('Arial', 9, 'bold')).grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(10, 2))
        
        self.headers_text = scrolledtext.ScrolledText(builder_frame, height=12, width=65, font=('Consolas', 8))
        self.headers_text.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        self.headers_text.insert(tk.END, '{\n  "Content-Type": "application/json",\n  "X-XSRF-TOKEN": "{{xsrf_token}}"\n}')
        
        # Headers Save Button
        self.save_headers_button = ttk.Button(builder_frame, text="💾 Save Headers", command=self.save_headers, state=tk.NORMAL)
        self.save_headers_button.grid(row=7, column=0, sticky=tk.W, pady=2)
        
        # Body
        self.body_label = ttk.Label(builder_frame, text="Request Body:", font=('Arial', 9, 'bold'))
        self.body_label.grid(row=8, column=0, columnspan=2, sticky=tk.W, pady=(10, 2))
        
        self.body_text = scrolledtext.ScrolledText(builder_frame, height=18, width=65, font=('Consolas', 8))
        self.body_text.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        self.body_text.insert(tk.END, '{\n  "example": "value"\n}')
        
        # Body Save Button
        self.save_body_button = ttk.Button(builder_frame, text="💾 Save Body", command=self.save_body, state=tk.NORMAL)
        self.save_body_button.grid(row=10, column=0, sticky=tk.W, pady=2)
        
        # Parameters
        self.params_label = ttk.Label(builder_frame, text="Query Parameters:", font=('Arial', 9, 'bold'))
        self.params_label.grid(row=11, column=0, columnspan=2, sticky=tk.W, pady=(10, 2))
        
        self.params_text = scrolledtext.ScrolledText(builder_frame, height=12, width=65, font=('Consolas', 8))
        self.params_text.grid(row=12, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        self.params_text.insert(tk.END, 'param1=value1&param2=value2')
        
        # Parameters Save Button
        self.save_params_button = ttk.Button(builder_frame, text="💾 Save Parameters", command=self.save_params, state=tk.NORMAL)
        self.save_params_button.grid(row=13, column=0, sticky=tk.W, pady=2)
        
        # Send button
        self.send_button = ttk.Button(builder_frame, text="Send Request", command=self.send_custom_request, state=tk.NORMAL)
        self.send_button.grid(row=14, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        # Grid weights
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        builder_frame.columnconfigure(1, weight=1)
    
    def create_right_panel(self, parent):
        # Results section - Modern style (compact)
        results_frame = ttk.LabelFrame(parent, text="📊 Results", padding="10")
        results_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Toolbar
        toolbar = ttk.Frame(results_frame)
        toolbar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(toolbar, text="Clear", command=self.clear_results).grid(row=0, column=0, padx=2)
        ttk.Button(toolbar, text="Export", command=self.export_results).grid(row=0, column=1, padx=2)
        ttk.Button(toolbar, text="Copy", command=self.copy_results).grid(row=0, column=2, padx=2)
        
        # Results text with better sizing and scrollbar
        self.result_text = scrolledtext.ScrolledText(results_frame, width=90, height=50, wrap=tk.WORD, font=('Consolas', 9))
        self.result_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 0), pady=(0, 0))
        
        # Grid weights
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)
    
    
    def on_category_select(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            category_name = event.widget.get(index)
            
            # Check if "No collection imported" message is selected
            if category_name == "⚠️ No collection imported":
                self.log_message("⚠️ Please import an API collection first")
                return
            
            # Handle main category selection (📁 prefix)
            if category_name.startswith("📁 "):
                # Extract main category name
                main_category = category_name.replace("📁 ", "", 1).split(" (")[0]
                
                # Toggle expansion of this category
                if main_category in self.expanded_categories:
                    # Collapse - remove subcategories
                    self._collapse_category(main_category)
                else:
                    # Expand - show subcategories
                    self._expand_category(main_category)
                    
                # Show all methods from this main category (including nested subcategories)
                self.method_listbox.delete(0, tk.END)
                all_methods = []
                for cat_key, methods in self.imported_apis.items():
                    if cat_key == main_category or cat_key.startswith(f"{main_category}|"):
                        all_methods.extend(list(methods.keys()))
                
                # Display in original order without de-duplication
                for method_name in all_methods:
                    self.method_listbox.insert(tk.END, method_name)
                
                self.log_message(f"📋 Loaded {len(all_methods)} methods from category: {main_category}")
                self.selected_category = main_category
                
                # Auto-select first method if available
                if all_methods:
                    self.method_listbox.selection_set(0)
                    self.on_method_select(None)  # Trigger method selection
            
            # Handle subcategory selection (📂 prefix)
            elif category_name.startswith("  📂 "):
                # Subcategory selected - show only methods in this subcategory
                subcategory_info = category_name.replace("  📂 ", "", 1)
                subcategory = subcategory_info.split(" (")[0]
                
                # Find the parent category and get methods from imported_apis
                for main_category in self.category_structure.keys():
                    if subcategory in self.category_structure[main_category]:
                        # Get methods for this specific subcategory from imported_apis
                        subcategory_key = f"{main_category}|{subcategory}"
                        if subcategory_key in self.imported_apis:
                            filtered_methods = list(self.imported_apis[subcategory_key].keys())
                            
                            if filtered_methods:
                                # Clear method list and add filtered methods
                                self.method_listbox.delete(0, tk.END)
                                for method_name in filtered_methods:
                                    self.method_listbox.insert(tk.END, method_name)
                                self.log_message(f"📋 Loaded {len(filtered_methods)} methods from subcategory: {subcategory}")
                                self.selected_category = subcategory_key  # Use full key for subcategory
                                
                                # Auto-select first method if available
                                if filtered_methods:
                                    self.method_listbox.selection_set(0)
                                    self.on_method_select(None)  # Trigger method selection
                                break
                        else:
                            self.log_message(f"⚠️ No methods found for subcategory: {subcategory}")
                            break
                else:
                    self.log_message(f"⚠️ No methods found for subcategory: {subcategory}")
            else:
                # Legacy format or other cases
                if category_name in self.imported_apis:
                    methods = list(self.imported_apis[category_name].keys())
                    for method_name in methods:
                        self.method_listbox.insert(tk.END, method_name)
                    self.log_message(f"📋 Loaded {len(methods)} methods from category: {category_name}")
                    self.selected_category = category_name
                    
                    # Auto-select first method if available
                    if methods:
                        self.method_listbox.selection_set(0)
                        self.on_method_select(None)  # Trigger method selection
                else:
                    self.log_message(f"⚠️ No methods found for category: {category_name}")
    
    def _expand_category(self, main_category):
        """Expand a category to show its subcategories"""
        if main_category not in self.category_structure:
            return
        
        # Find the category index in the listbox
        category_index = None
        for i in range(self.category_listbox.size()):
            item = self.category_listbox.get(i)
            if item.startswith("📁 ") and main_category in item:
                category_index = i
                break
        
        if category_index is None:
            return
        
        # Add subcategories after the main category
        subcategories = self.category_structure[main_category]
        insert_index = category_index + 1
        
        for subcategory in sorted(subcategories.keys()):
            method_count = len(subcategories[subcategory])
            self.category_listbox.insert(insert_index, f"  📂 {subcategory} ({method_count} methods)")
            insert_index += 1
        
        # Mark as expanded
        self.expanded_categories.add(main_category)
        self.log_message(f"📂 Expanded category: {main_category}")
    
    def _collapse_category(self, main_category):
        """Collapse a category to hide its subcategories"""
        if main_category not in self.category_structure:
            return
        
        # Find and remove subcategories
        items_to_remove = []
        for i in range(self.category_listbox.size()):
            item = self.category_listbox.get(i)
            if item.startswith("  📂 "):
                # Check if this subcategory belongs to the main category
                subcategory_name = item.replace("  📂 ", "", 1).split(" (")[0]
                if subcategory_name in self.category_structure[main_category]:
                    items_to_remove.append(i)
        
        # Remove subcategories (in reverse order to maintain indices)
        for i in reversed(items_to_remove):
            self.category_listbox.delete(i)
        
        # Mark as collapsed
        self.expanded_categories.discard(main_category)
        self.log_message(f"📁 Collapsed category: {main_category}")
    
    def on_method_select(self, event):
        if event is None:
            # Called programmatically, select first item
            if self.method_listbox.size() > 0:
                self.method_listbox.selection_set(0)
                self.selected_method = self.method_listbox.get(0)
            else:
                return
        else:
            selection = event.widget.curselection()
            if selection:
                index = selection[0]
                self.selected_method = event.widget.get(index)
            else:
                return
        
        # Find the correct category for this method
        if self.selected_method and self.selected_category:
            # Look for the method in the imported APIs
            for category_key in self.imported_apis.keys():
                if self.selected_method in self.imported_apis[category_key]:
                    # Update selected_category to the actual category key
                    self.selected_category = category_key
                    self.log_message(f"🔍 Found method '{self.selected_method}' in category: {category_key}")
                    break
        
        # Activate save buttons
        self.save_headers_button.config(state=tk.NORMAL)
        self.save_body_button.config(state=tk.NORMAL)
        self.save_params_button.config(state=tk.NORMAL)
        self.save_url_button.config(state=tk.NORMAL)
        self.save_path_button.config(state=tk.NORMAL)
        
        # Load template automatically
        self.load_template()
    
    def test_api_method(self):
        if not self.selected_category or not self.selected_method:
            messagebox.showerror("Error", "Please select a category and method")
            return
        
        # Get API info from imported APIs
        if self.selected_category in self.imported_apis and self.selected_method in self.imported_apis[self.selected_category]:
            api_info = self.imported_apis[self.selected_category][self.selected_method]
        else:
            messagebox.showerror("Error", "Selected method not found")
            return
        
        # Get base URL from method info or use default
        base_url = api_info.get('base_url', 'https://api.example.com')
        url_path = api_info.get('url_path', '/')
        method = api_info.get('method', 'GET')
        
        # Construct full URL
        if url_path.startswith('http'):
            url = url_path
        else:
            url = f"{base_url}{url_path}"
        
        # Get headers and body
        headers = api_info.get('headers', {})
        body = api_info.get('body', '')
        params = api_info.get('params', '')
        
        try:
            self.log_message(f"Testing {method} {url}...")
            
            # Make request based on method
            if method.upper() == 'GET':
                # Parse URL-encoded parameters
                parsed_params = {}
                if params:
                    from urllib.parse import parse_qs
                    parsed_params = parse_qs(params)
                    # Convert from {key: [value]} to {key: value} format
                    parsed_params = {key: value[0] if len(value) == 1 else value for key, value in parsed_params.items()}
                response = self.session.get(url, headers=headers, params=parsed_params, verify=False)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=json.loads(body) if body else None, headers=headers, verify=False)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=json.loads(body) if body else None, headers=headers, verify=False)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, headers=headers, verify=False)
            else:
                response = self.session.request(method, url, headers=headers, verify=False)
            
            # Log response details
            self.log_message(f"📊 Status Code: {response.status_code}")
            self.log_message(f"⏱️ Response Time: {response.elapsed.total_seconds():.3f}s")
            
            # Log response headers
            self.log_message(f"📋 Response Headers:")
            for key, value in response.headers.items():
                self.log_message(f"   {key}: {value}")
            
            # Log response body
            try:
                if response.text:
                    response_json = response.json()
                    formatted_json = json.dumps(response_json, indent=2, ensure_ascii=False)
                    self.log_message(f"📄 Response Body:\n{formatted_json}")
                else:
                    self.log_message("📄 Response Body: (Empty)")
            except:
                self.log_message(f"📄 Response Body: {response.text}")
            
            # Store authentication tokens if present
            if 'XSRF-TOKEN' in response.cookies:
                self.xsrf_token = response.cookies['XSRF-TOKEN']
                self.log_message(f"🔐 XSRF Token stored: {self.xsrf_token[:20]}...")
            
            # Store session ID if present in response
            try:
                response_data = response.json()
                if 'sessionId' in response_data:
                    self.session_id = response_data['sessionId']
                    self.log_message(f"🔑 Session ID stored: {self.session_id[:20]}...")
            except:
                pass
            
            # Enable buttons
            self.send_button.config(state=tk.NORMAL)
            self.load_template_button.config(state=tk.NORMAL)
            self.run_automation_button.config(state=tk.NORMAL)
            
            self.log_message("✅ API test completed!")
        
        except Exception as e:
            self.log_message(f"❌ API test error: {str(e)}")
            messagebox.showerror("Error", f"API test failed: {str(e)}")
    
    def test_api(self):
        if not self.selected_category or not self.selected_method:
            messagebox.showwarning("Warning", "Please select a category and method")
            return
        
        self.execute_api_test(self.selected_category, self.selected_method)
    
    def test_all_apis(self):
        self.log_message("\n" + "="*80)
        self.log_message("STARTING FULL API TEST")
        self.log_message("="*80 + "\n")
        
        for category, methods in self.imported_apis.items():
            self.log_message(f"\n{'='*80}")
            self.log_message(f"Testing Category: {category}")
            self.log_message(f"{'='*80}\n")
            
            for method_name in methods.keys():
                self.execute_api_test(category, method_name)
                self.root.update()
        
        self.log_message("\n" + "="*80)
        self.log_message("FULL API TEST COMPLETED")
        self.log_message("="*80 + "\n")
    
    def execute_api_test(self, category: str, method_name: str):
        # Get API info - only from imported APIs
        if category in self.imported_apis:
            api_info = self.imported_apis[category][method_name]
        else:
            self.log_message(f"❌ API method not found: {category} - {method_name}")
            return False
        
        method = api_info["method"]
        path = api_info["path"]
        
        # Get base URL from API info or use default
        base_url = api_info.get('base_url', 'https://api.example.com')
        
        # Construct full URL
        if path.startswith('http'):
            url = path
        else:
            url = f"{base_url}{path}"
        
        # Get headers from API info
        headers = api_info.get("headers", {})
        headers["Content-Type"] = "application/json"
        
        # Clean Postman variables from headers
        cleaned_headers = {}
        for key, value in headers.items():
            if isinstance(value, str):
                cleaned_value = self._clean_postman_variables(value)
                cleaned_headers[key] = cleaned_value
            else:
                cleaned_headers[key] = value
        
        headers = cleaned_headers
        
        # Add authentication headers
        self._add_auth_headers(headers, "test request")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_message(f"\n{'═'*100}")
        self.log_message(f"🕐 {timestamp} | Testing: {category} > {method_name}")
        self.log_message(f"📡 Method: {method}")
        self.log_message(f"🔗 URL: {url}")
        self.log_message(f"{'═'*100}")
        
        try:
            # Make API call
            if method == "GET":
                params = api_info.get("params", {})
                response = self.session.get(url, headers=headers, params=params, verify=False, timeout=30)
            elif method == "POST":
                response = self.session.post(url, headers=headers, json={}, verify=False, timeout=30)
            elif method == "PUT":
                response = self.session.put(url, headers=headers, json={}, verify=False, timeout=30)
            elif method == "DELETE":
                response = self.session.delete(url, headers=headers, verify=False, timeout=30)
            else:
                self.log_message(f"❌ Unsupported method: {method}")
                return False
            
            # Log result in detail
            success = response.status_code < 400
            status_icon = "✅" if success else "❌"
            self.log_message(f"\n{status_icon} STATUS CODE: {response.status_code}")
            self.log_message(f"📊 RESPONSE TIME: {response.elapsed.total_seconds():.3f}s")
            
            # Show headers
            self.log_message(f"\n📋 RESPONSE HEADERS:")
            for key, value in response.headers.items():
                self.log_message(f"   {key}: {value}")
            
            # Automatically extract and store XSRF token
            if 'XSRF-TOKEN' in response.headers:
                new_xsrf_token = response.headers['XSRF-TOKEN']
                if new_xsrf_token and new_xsrf_token != self.xsrf_token:
                    self.xsrf_token = new_xsrf_token
                    self.log_message(f"🔐 XSRF Token updated from header: {self.xsrf_token[:20]}...")
            
            # Extract XSRF token from Set-Cookie header
            if 'Set-Cookie' in response.headers:
                set_cookie = response.headers['Set-Cookie']
                if 'XSRF-TOKEN=' in set_cookie:
                    # Extract XSRF token from Set-Cookie header
                    import re
                    match = re.search(r'XSRF-TOKEN=([^;]+)', set_cookie)
                    if match:
                        new_xsrf_token = match.group(1)
                        if new_xsrf_token and new_xsrf_token != self.xsrf_token:
                            self.xsrf_token = new_xsrf_token
                            self.log_message(f"🔐 XSRF Token extracted from Set-Cookie: {self.xsrf_token[:20]}...")
            
            # Debug: Show current XSRF token status
            if self.xsrf_token:
                self.log_message(f"🔐 Current XSRF Token: {self.xsrf_token[:20]}...")
            else:
                self.log_message("⚠️ No XSRF Token available")
            
            # Show response body in detail
            if response.text:
                self.log_message(f"\n📄 RESPONSE BODY:")
                try:
                    response_json = response.json()
                    formatted_json = json.dumps(response_json, indent=2, ensure_ascii=False)
                    self.log_message(formatted_json)
                except:
                    self.log_message(response.text)
            else:
                self.log_message("📄 RESPONSE BODY: (Empty)")
            
            # Show request details
            self.log_message(f"\n📤 REQUEST DETAILS:")
            self.log_message(f"   Headers: {json.dumps(headers, indent=2)}")
            if method == "GET" and api_info.get("params"):
                self.log_message(f"   Query Params: {json.dumps(api_info['params'], indent=2)}")
            
            self.log_message(f"\n{'─'*100}")
            return success
        
        except requests.exceptions.Timeout:
            self.log_message(f"⏰ Timeout error (30 seconds)")
            return False
        except Exception as e:
            self.log_message(f"💥 Error: {str(e)}")
            import traceback
            self.log_message(f"📋 Traceback: {traceback.format_exc()}")
            return False
    
    def execute_api_test_with_template(self, category: str, method_name: str, template_key: str):
        """Dynamic template ile API test et"""
        template = self.dynamic_templates[template_key]
        method = template["method"]
        base_url = template.get('base_url', 'https://api.example.com')
        path = template.get('path', '/')
        
        # Construct full URL - path should never be a full URL, only path portion
        # Ensure base_url ends with / and path starts with /
        if not base_url.endswith('/') and not path.startswith('/'):
            url = f"{base_url}/{path}"
        elif base_url.endswith('/') and path.startswith('/'):
            url = f"{base_url}{path[1:]}"
        else:
            url = f"{base_url}{path}"
        
        # Parse headers
        try:
            headers = json.loads(template["headers"]) if template["headers"] else {}
        except:
            headers = {"Content-Type": "application/json"}
        
        # Clean Postman variables from headers
        cleaned_headers = {}
        for key, value in headers.items():
            if isinstance(value, str):
                cleaned_value = self._clean_postman_variables(value)
                cleaned_headers[key] = cleaned_value
            else:
                cleaned_headers[key] = value
        
        headers = cleaned_headers
        
        # Add authentication tokens to headers
        self._add_auth_headers(headers, "automation request")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_message(f"\n{'═'*100}")
        self.log_message(f"🕐 {timestamp} | Testing: {category} > {method_name} (Dynamic Template)")
        self.log_message(f"📡 Method: {method}")
        self.log_message(f"🔗 URL: {url}")
        self.log_message(f"{'═'*100}")
        
        try:
            # Make API call
            if method == "GET":
                # Parse URL-encoded parameters
                params = {}
                if template["params"]:
                    from urllib.parse import parse_qs
                    parsed_params = parse_qs(template["params"])
                    params = {key: value[0] if len(value) == 1 else value for key, value in parsed_params.items()}
                response = self.session.get(url, headers=headers, params=params, verify=False, timeout=30)
            elif method == "POST":
                body = json.loads(template["body"]) if template["body"] else {}
                response = self.session.post(url, headers=headers, json=body, verify=False, timeout=30)
            elif method == "PUT":
                body = json.loads(template["body"]) if template["body"] else {}
                response = self.session.put(url, headers=headers, json=body, verify=False, timeout=30)
            elif method == "DELETE":
                # For DELETE method, use body if available, otherwise use params
                if template["body"]:
                    body = json.loads(template["body"])
                    response = self.session.delete(url, headers=headers, json=body, verify=False, timeout=30)
                elif template["params"]:
                    # Parse URL-encoded parameters
                    from urllib.parse import parse_qs
                    parsed_params = parse_qs(template["params"])
                    params = {key: value[0] if len(value) == 1 else value for key, value in parsed_params.items()}
                    response = self.session.delete(url, headers=headers, params=params, verify=False, timeout=30)
                else:
                    response = self.session.delete(url, headers=headers, verify=False, timeout=30)
            else:
                self.log_message(f"❌ Unsupported method: {method}")
                return False
            
            # Log result in detail
            success = response.status_code < 400
            status_icon = "✅" if success else "❌"
            self.log_message(f"\n{status_icon} STATUS CODE: {response.status_code}")
            self.log_message(f"📊 RESPONSE TIME: {response.elapsed.total_seconds():.3f}s")
            
            # Show headers
            self.log_message(f"\n📋 RESPONSE HEADERS:")
            for key, value in response.headers.items():
                self.log_message(f"   {key}: {value}")
            # Extract authentication tokens from response
            self._extract_auth_tokens(response)
            
            # Show response body in detail
            if response.text:
                self.log_message(f"\n📄 RESPONSE BODY:")
                try:
                    response_json = response.json()
                    formatted_json = json.dumps(response_json, indent=2, ensure_ascii=False)
                    self.log_message(formatted_json)
                except:
                    self.log_message(response.text)
            else:
                self.log_message("📄 RESPONSE BODY: (Empty)")
            
            # Show request details
            self.log_message(f"\n📤 REQUEST DETAILS (Dynamic Template):")
            self.log_message(f"   Headers: {json.dumps(headers, indent=2)}")
            if template["body"]:
                try:
                    body_data = json.loads(template["body"])
                    self.log_message(f"   Body: {json.dumps(body_data, indent=2)}")
                except:
                    self.log_message(f"   Body: {template['body']}")
            if template["params"]:
                self.log_message(f"   Query Params: {template['params']}")
            
            self.log_message(f"\n{'─'*100}")
            return success
        
        except requests.exceptions.Timeout:
            self.log_message(f"⏰ Timeout error (30 seconds)")
            return False
        except Exception as e:
            self.log_message(f"💥 Error: {str(e)}")
            import traceback
            self.log_message(f"📋 Traceback: {traceback.format_exc()}")
            return False
    
    def log_message(self, message: str):
        self.result_text.insert(tk.END, message + "\n")
        self.result_text.see(tk.END)
        self.root.update()
    
    def send_custom_request(self):
        """Custom request builder ile API çağrısı yap"""
        method = self.method_combo.get()
        base_url = self.base_url_entry.get().strip()
        path = self.path_entry.get().strip()
        
        if not base_url:
            messagebox.showwarning("Warning", "Please enter Base URL")
            return
        
        if not path:
            messagebox.showwarning("Warning", "Please enter Path")
            return
        
        # Construct full URL - path should never be a full URL, only path portion
        # Ensure base_url ends with / and path starts with /
        if not base_url.endswith('/') and not path.startswith('/'):
            url = f"{base_url}/{path}"
        elif base_url.endswith('/') and path.startswith('/'):
            url = f"{base_url}{path[1:]}"
        else:
            url = f"{base_url}{path}"
        
        # Validate URL format
        if not self._is_valid_url(url):
            messagebox.showerror("Error", f"Invalid URL format: {url}\nPlease check Base URL and Path fields.")
            return
        
        # Parse headers
        try:
            headers_text = self.headers_text.get("1.0", tk.END).strip()
            headers = json.loads(headers_text) if headers_text else {}
            
            # Clean Postman variables from headers
            cleaned_headers = {}
            for key, value in headers.items():
                if isinstance(value, str):
                    cleaned_value = self._clean_postman_variables(value)
                    cleaned_headers[key] = cleaned_value
                else:
                    cleaned_headers[key] = value
            
            headers = cleaned_headers
            
            # Add authentication headers
            self._add_auth_headers(headers, "request")
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid JSON in headers")
            return
        
        # Parse body - if field is visible
        body = {}
        if self.body_text.winfo_viewable():
            try:
                body_text = self.body_text.get("1.0", tk.END).strip()
                body = json.loads(body_text) if body_text else {}
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Invalid JSON in request body")
                return
        
        # Parse parameters - if field is visible
        params = {}
        if self.params_text.winfo_viewable():
            try:
                params_text = self.params_text.get("1.0", tk.END).strip()
                if params_text:
                    # Parse URL-encoded parameters (param1=value1&param2=value2)
                    from urllib.parse import parse_qs, unquote
                    # Use parse_qs to handle URL-encoded parameters
                    parsed_params = parse_qs(params_text)
                    # Convert from {key: [value]} to {key: value} format
                    params = {key: value[0] if len(value) == 1 else value for key, value in parsed_params.items()}
            except Exception as e:
                messagebox.showerror("Error", f"Invalid query parameters format: {str(e)}")
                return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_message(f"\n{'═'*100}")
        self.log_message(f"🕐 {timestamp} | Custom Request")
        self.log_message(f"📡 Method: {method}")
        self.log_message(f"🔗 URL: {url}")
        self.log_message(f"{'═'*100}")
        
        try:
            # Make API call
            if method == "GET":
                response = self.session.get(url, headers=headers, params=params, verify=False, timeout=30)
            elif method == "POST":
                response = self.session.post(url, headers=headers, json=body, params=params, verify=False, timeout=30)
            elif method == "PUT":
                response = self.session.put(url, headers=headers, json=body, params=params, verify=False, timeout=30)
            elif method == "DELETE":
                # For DELETE method, use body if available, otherwise use params
                if body:
                    response = self.session.delete(url, headers=headers, json=body, verify=False, timeout=30)
                elif params:
                    response = self.session.delete(url, headers=headers, params=params, verify=False, timeout=30)
                else:
                    response = self.session.delete(url, headers=headers, verify=False, timeout=30)
            else:
                self.log_message(f"❌ Unsupported method: {method}")
                return
            
            # Log result in detail
            status_icon = "✅" if response.status_code < 400 else "❌"
            self.log_message(f"\n{status_icon} STATUS CODE: {response.status_code}")
            self.log_message(f"📊 RESPONSE TIME: {response.elapsed.total_seconds():.3f}s")
            
            # Show headers
            self.log_message(f"\n📋 RESPONSE HEADERS:")
            for key, value in response.headers.items():
                self.log_message(f"   {key}: {value}")
            
            # Automatically extract and store XSRF token
            if 'XSRF-TOKEN' in response.headers:
                new_xsrf_token = response.headers['XSRF-TOKEN']
                if new_xsrf_token and new_xsrf_token != self.xsrf_token:
                    self.xsrf_token = new_xsrf_token
                    self.log_message(f"🔐 XSRF Token updated from header: {self.xsrf_token[:20]}...")
            
            # Extract XSRF token from Set-Cookie header
            if 'Set-Cookie' in response.headers:
                set_cookie = response.headers['Set-Cookie']
                if 'XSRF-TOKEN=' in set_cookie:
                    # Extract XSRF token from Set-Cookie header
                    import re
                    match = re.search(r'XSRF-TOKEN=([^;]+)', set_cookie)
                    if match:
                        new_xsrf_token = match.group(1)
                        if new_xsrf_token and new_xsrf_token != self.xsrf_token:
                            self.xsrf_token = new_xsrf_token
                            self.log_message(f"🔐 XSRF Token extracted from Set-Cookie: {self.xsrf_token[:20]}...")
            
            # Debug: Show current XSRF token status
            if self.xsrf_token:
                self.log_message(f"🔐 Current XSRF Token: {self.xsrf_token[:20]}...")
            else:
                self.log_message("⚠️ No XSRF Token available")
            
            # Show response body in detail
            if response.text:
                self.log_message(f"\n📄 RESPONSE BODY:")
                try:
                    response_json = response.json()
                    formatted_json = json.dumps(response_json, indent=2, ensure_ascii=False)
                    self.log_message(formatted_json)
                except:
                    self.log_message(response.text)
            else:
                self.log_message("📄 RESPONSE BODY: (Empty)")
            
            # Show request details
            self.log_message(f"\n📤 REQUEST DETAILS:")
            self.log_message(f"   Headers: {json.dumps(headers, indent=2)}")
            if body:
                self.log_message(f"   Body: {json.dumps(body, indent=2)}")
            if params:
                self.log_message(f"   Query Params: {json.dumps(params, indent=2)}")
            
            self.log_message(f"\n{'─'*100}")
        
        except requests.exceptions.Timeout:
            self.log_message(f"⏰ Timeout error (30 seconds)")
        except Exception as e:
            self.log_message(f"💥 Error: {str(e)}")
            import traceback
            self.log_message(f"📋 Traceback: {traceback.format_exc()}")
    
    def load_template(self):
        """Load template from selected API"""
        if not self.selected_category or not self.selected_method:
            messagebox.showwarning("Warning", "Please select an API method first")
            return

        # Get API info - only from imported APIs
        if self.selected_category in self.imported_apis:
            api_info = self.imported_apis[self.selected_category][self.selected_method]
        else:
            messagebox.showerror("Error", "API method not found")
            return

        # Method'u set et
        self.method_combo.set(api_info["method"])

        # Set base URL - use baseUrl variable from collection
        method_key = f"{self.selected_category} - {self.selected_method}"
        
        if method_key in self.saved_urls:
            # Save edilen URL'yi kullan
            self.base_url_entry.delete(0, tk.END)
            self.base_url_entry.insert(0, self.saved_urls[method_key])
            self.log_message(f"💾 Loaded saved URL for: {self.selected_method}")
        else:
            # Use baseUrl variable from collection
            collection_base_url = self.collection_variables.get('baseUrl', '')
            if collection_base_url:
                self.base_url_entry.delete(0, tk.END)
                self.base_url_entry.insert(0, collection_base_url)
                self.log_message(f"🔗 Loaded base URL from collection: {collection_base_url}")
            else:
                # Fallback to API info if no collection variable
                base_url = api_info.get("base_url", "")
                if base_url:
                    cleaned_base_url = self._clean_postman_variables(base_url)
                    self.base_url_entry.delete(0, tk.END)
                    self.base_url_entry.insert(0, cleaned_base_url)
                    self.log_message(f"🔗 Loaded base URL from API info: {cleaned_base_url}")
                else:
                    self.log_message("⚠️ No base URL found in collection or API info")

        # Set path - use saved one if available, otherwise use path from API
        if method_key in self.saved_paths:
            # Save edilen path'i kullan
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, self.saved_paths[method_key])
            self.log_message(f"💾 Loaded saved path for: {self.selected_method}")
        else:
            # Use path from API - take only the path part
            original_path = api_info.get("path", "/")
            path = self._extract_path_from_url(original_path)
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)

        # Set headers - use saved ones if available, otherwise use headers from API
        
        if method_key in self.saved_headers:
            # Use saved headers
            self.headers_text.delete("1.0", tk.END)
            self.headers_text.insert("1.0", self.saved_headers[method_key])
            self.log_message(f"💾 Loaded saved headers for: {self.selected_method}")
        else:
            # Use headers from API, automatically add XSRF token
            headers = api_info.get("headers", {})
            
            # Clean Postman variables from headers
            cleaned_headers = {}
            for key, value in headers.items():
                if isinstance(value, str):
                    cleaned_value = self._clean_postman_variables(value)
                    cleaned_headers[key] = cleaned_value
                else:
                    cleaned_headers[key] = value
            
            headers = cleaned_headers
            
            if self.xsrf_token:
                headers["X-XSRF-TOKEN"] = self.xsrf_token
            else:
                headers["X-XSRF-TOKEN"] = "{{xsrf_token}}"

            self.headers_text.delete("1.0", tk.END)
            self.headers_text.insert("1.0", json.dumps(headers, indent=2))

        # Set body - use saved one if available, otherwise use body from API
        if method_key in self.saved_bodies:
            # Save edilen body'yi kullan
            self.body_text.delete("1.0", tk.END)
            self.body_text.insert("1.0", self.saved_bodies[method_key])
            self.log_message(f"💾 Loaded saved body for: {self.selected_method}")
        else:
            # Use body from API
            body = api_info.get("body", "")
            if body:
                # Try to prettify JSON if it's valid JSON
                try:
                    if isinstance(body, str):
                        parsed_body = json.loads(body)
                        prettified_body = json.dumps(parsed_body, indent=2, ensure_ascii=False)
                    else:
                        prettified_body = json.dumps(body, indent=2, ensure_ascii=False)
                    self.body_text.delete("1.0", tk.END)
                    self.body_text.insert("1.0", prettified_body)
                except (json.JSONDecodeError, TypeError):
                    # If not valid JSON, use as is
                    self.body_text.delete("1.0", tk.END)
                    self.body_text.insert("1.0", body)
            elif api_info["method"] in ["POST", "PUT"]:
                self.body_text.delete("1.0", tk.END)
                self.body_text.insert("1.0", json.dumps({}, indent=2))

        # Set parameters - use saved ones if available, otherwise use params from API
        if method_key in self.saved_params:
            # Use saved params
            self.params_text.delete("1.0", tk.END)
            self.params_text.insert("1.0", self.saved_params[method_key])
            self.log_message(f"💾 Loaded saved params for: {self.selected_method}")
        else:
            # Use params from API
            params = api_info.get("params", {})
            if params:
                self.params_text.delete("1.0", tk.END)
                # Convert params dict to URL-encoded format
                from urllib.parse import urlencode
                params_string = urlencode(params)
                self.params_text.insert("1.0", params_string)

        # Show/hide fields according to method type
        self._update_field_visibility(api_info)

        # Update dynamic template
        self._update_dynamic_template()

        self.log_message(f"✓ Template loaded for: {self.selected_method}")
    
    def import_api_collection(self):
        """Import APIs from API collection"""
        from tkinter import filedialog
        
        # Open file dialog
        file_path = filedialog.askopenfilename(
            title="Select API Collection File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            self.log_message("📥 Importing API collection...")
            
            # Read JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                collection_data = json.load(f)
            
            # First find categories in collection
            available_categories = self._find_categories_in_collection(collection_data)
            
            if not available_categories:
                self.log_message("⚠️ No categories found in the collection.")
                self.import_status_label.config(text="⚠️ No categories found", foreground="orange")
                return
            
            # Show category selection dialog
            selected_categories = self._show_category_selection_dialog(available_categories)
            
            if not selected_categories:
                self.log_message("❌ No categories selected. Import cancelled.")
                return
            
            # Import selected categories
            imported_count = self._parse_api_collection(collection_data, selected_categories)
            
            if imported_count > 0:
                self.collection_loaded = True
                self.log_message(f"✅ Successfully imported {imported_count} API methods from {len(selected_categories)} categories!")
                self.log_message(f"📊 Imported categories: {list(self.imported_apis.keys())}")
                
                # Clear method list (remove old values)
                self.method_listbox.delete(0, tk.END)
                self.selected_category = ""
                self.selected_method = ""
                
                # Update import status
                self.import_status_label.config(text=f"✅ {imported_count} APIs imported", foreground="green")
                self.remove_collection_button.config(state=tk.NORMAL)
                self.export_collection_button.config(state=tk.NORMAL)
                
                # Update category list
                self._update_category_list()
                
                # Butonlar hep aktif kalacak
                
                # Update UI
                self.root.update_idletasks()
                
                self.log_message("🔄 Method list cleared. Please select a category to see imported methods.")
            else:
                self.log_message("⚠️ No APIs found in the selected categories.")
                self.import_status_label.config(text="⚠️ No APIs found", foreground="orange")
                
        except Exception as e:
            self.log_message(f"❌ Error importing collection: {str(e)}")
            import traceback
            self.log_message(f"📋 Traceback: {traceback.format_exc()}")
    
    def remove_collection(self):
        """Import edilen collection'ı kaldır"""
        if not self.collection_loaded:
            messagebox.showinfo("Info", "No collection to remove")
            return
        
        # Onay al
        result = messagebox.askyesno("Confirm", "Are you sure you want to remove the imported collection?")
        if not result:
            return
        
        # Clear collection
        self.imported_apis = {}
        self.category_structure = {}
        self.expanded_categories.clear()
        self.collection_loaded = False
        self.collection_variables = {}
        self.auth_token = ""  # Clear auth token when collection is removed
        
        # Update status
        self.import_status_label.config(text="No collection imported", foreground="gray")
        # Remove button stays active
        self.export_collection_button.config(state=tk.DISABLED)
        
        # Method listesini temizle
        self.method_listbox.delete(0, tk.END)
        self.selected_category = ""
        self.selected_method = ""
        
        # Update category list
        self._update_category_list()
        
        # Clear all form fields
        self._clear_all_fields()
        
        # Automation listesini temizle
        self.automation_methods.clear()
        self.method_order_listbox.delete(0, tk.END)
        
        # Dynamic templates'i temizle
        self.dynamic_templates.clear()
        
        # Clear saved values
        self.saved_headers.clear()
        self.saved_bodies.clear()
        self.saved_params.clear()
        self.saved_urls.clear()
        self.saved_paths.clear()
        
        self.log_message("🗑️ Imported collection removed successfully!")
        self.log_message("🔄 All fields cleared. Please import a new collection.")
    
    def _clear_all_fields(self):
        """Clear all form fields"""
        # Clear method selection
        self.method_combo.set("GET")
        
        # Clear URL and Path fields
        self.base_url_entry.delete(0, tk.END)
        self.path_entry.delete(0, tk.END)
        
        # Clear text fields
        self.headers_text.delete("1.0", tk.END)
        self.body_text.delete("1.0", tk.END)
        self.params_text.delete("1.0", tk.END)
        
        # Disable save buttons
        self.save_headers_button.config(state=tk.DISABLED)
        self.save_body_button.config(state=tk.DISABLED)
        self.save_params_button.config(state=tk.DISABLED)
        self.save_url_button.config(state=tk.DISABLED)
        self.save_path_button.config(state=tk.DISABLED)
    
    def export_api_collection(self):
        """Export current APIs with saved URL and Path to Postman collection"""
        if not self.collection_loaded:
            messagebox.showinfo("Info", "No collection to export")
            return
        
        from tkinter import filedialog
        
        # Open file dialog
        file_path = filedialog.asksaveasfilename(
            title="Export API Collection",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            self.log_message("📤 Exporting API collection with saved URL and Path...")
            
            # Create Postman collection structure
            collection = {
                "info": {
                    "name": "Exported API Collection",
                    "description": "API collection exported from API Test Automation Tool",
                    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
                },
                "item": []
            }
            
            # Group categories by main category
            main_categories = {}
            for category_key in self.imported_apis.keys():
                methods = self.imported_apis[category_key]
                
                # Parse category key (format: "MainCategory|SubCategory" or just "MainCategory")
                if '|' in category_key:
                    main_category, subcategory = category_key.split('|', 1)
                else:
                    main_category = category_key
                    subcategory = "Main"
                
                # Initialize main category if not exists
                if main_category not in main_categories:
                    main_categories[main_category] = {}
                
                # Add subcategory to main category
                main_categories[main_category][subcategory] = methods
            
            # Create folder structure for each main category
            for main_category, subcategories in main_categories.items():
                folder = {
                    "name": main_category,
                    "item": []
                }
                
                # Add subcategories and their methods
                for subcategory, methods in subcategories.items():
                    if subcategory != "Main" or len(subcategories) == 1:
                        # Create subcategory folder or add methods directly
                        if subcategory != "Main":
                            subfolder = {
                                "name": subcategory,
                                "item": []
                            }
                        else:
                            subfolder = folder
                        
                        # Add methods to subcategory
                        for method_name, api_info in methods.items():
                            method_key = f"{category_key} - {method_name}"
                            
                            # Get saved values or use original values
                            saved_url = self.saved_urls.get(method_key, api_info.get('base_url', 'https://api.example.com'))
                            saved_path = self.saved_paths.get(method_key, api_info.get('path', '/'))
                            saved_headers = self.saved_headers.get(method_key, json.dumps(api_info.get('headers', {}), indent=2))
                            saved_body = self.saved_bodies.get(method_key, api_info.get('body', ''))
                            saved_params = self.saved_params.get(method_key, json.dumps(api_info.get('params', {}), indent=2))
                            
                            # Construct full URL - path should never be a full URL, only path portion
                            if not saved_url.endswith('/') and not saved_path.startswith('/'):
                                full_url = f"{saved_url}/{saved_path}"
                            elif saved_url.endswith('/') and saved_path.startswith('/'):
                                full_url = f"{saved_url}{saved_path[1:]}"
                            else:
                                full_url = f"{saved_url}{saved_path}"
                            
                            # Parse headers
                            try:
                                headers_dict = json.loads(saved_headers) if saved_headers else {}
                            except:
                                headers_dict = api_info.get('headers', {})
                            
                            # Parse body
                            try:
                                body_dict = json.loads(saved_body) if saved_body else {}
                            except:
                                body_dict = {}
                            
                            # Parse params (URL-encoded format)
                            params_dict = {}
                            if saved_params:
                                from urllib.parse import parse_qs
                                try:
                                    parsed_params = parse_qs(saved_params)
                                    params_dict = {key: value[0] if len(value) == 1 else value for key, value in parsed_params.items()}
                                except:
                                    params_dict = api_info.get('params', {})
                            else:
                                params_dict = api_info.get('params', {})
                            
                            # Create request item
                            request_item = {
                                "name": method_name,
                                "request": {
                                    "method": api_info.get('method', 'GET'),
                                    "header": [
                                        {
                                            "key": key,
                                            "value": value,
                                            "enabled": True
                                        }
                                        for key, value in headers_dict.items()
                                    ],
                                    "url": {
                                        "raw": full_url,
                                        "protocol": full_url.split('://')[0] if '://' in full_url else 'https',
                                        "host": full_url.split('://')[1].split('/')[0] if '://' in full_url else full_url.split('/')[0],
                                        "path": full_url.split('://')[1].split('/')[1:] if '://' in full_url and '/' in full_url.split('://')[1] else []
                                    }
                                }
                            }
                            
                            # Add body if present
                            if body_dict and api_info.get('method') in ['POST', 'PUT']:
                                request_item["request"]["body"] = {
                                    "mode": "raw",
                                    "raw": json.dumps(body_dict, indent=2)
                                }
                            
                            # Add query parameters if present
                            if params_dict:
                                request_item["request"]["url"]["query"] = [
                                    {
                                        "key": key,
                                        "value": value,
                                        "enabled": True
                                    }
                                    for key, value in params_dict.items()
                                ]
                            
                            subfolder["item"].append(request_item)
                        
                        # Add subfolder to main folder if it's a subcategory
                        if subcategory != "Main":
                            folder["item"].append(subfolder)
                    
                    # Add main folder to collection
                    collection["item"].append(folder)
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(collection, f, indent=2, ensure_ascii=False)
            
            self.log_message(f"✅ Successfully exported collection to: {file_path}")
            self.log_message(f"📊 Exported {len(self.imported_apis)} categories with saved URL and Path values")
            messagebox.showinfo("Success", f"Collection exported successfully to:\n{file_path}")
            
        except Exception as e:
            self.log_message(f"❌ Error exporting collection: {str(e)}")
            import traceback
            self.log_message(f"📋 Traceback: {traceback.format_exc()}")
            messagebox.showerror("Error", f"Failed to export collection: {str(e)}")
    
    def _find_categories_in_collection(self, collection_data):
        """Find all categories in the collection"""
        categories = set()  # Use set to avoid duplicates
        
        try:
            items = collection_data.get('item', [])
            self.log_message(f"🔍 Found {len(items)} items in collection")
            
            def process_items(items_list, level=0):
                for item in items_list:
                    if item.get('item'):  # This is a folder
                        folder_name = item.get('name', '')
                        if folder_name:
                            # Only add top-level folders to avoid duplicates
                            if level == 0:
                                categories.add(folder_name)
                                self.log_message(f"📁 Found main category: {folder_name}")
                            # Recursively process subfolders
                            process_items(item.get('item', []), level + 1)
                    else:
                        # Single request item
                        request_name = item.get('name', '')
                        self.log_message(f"📄 Found single request: {request_name}")
            
            process_items(items)
                        
        except Exception as e:
            self.log_message(f"❌ Error finding categories: {str(e)}")
            
        categories_list = list(categories)
        self.log_message(f"📋 Total main categories found: {len(categories_list)}")
        return categories_list
    
    def _show_category_selection_dialog(self, categories):
        """Show dialog to select categories"""
        from tkinter import simpledialog
        
        # Create a new window for category selection
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Categories to Import")
        dialog.configure(bg='#f8f9fa')
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Main container frame
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="📁 Select Categories to Import", font=('Arial', 12, 'bold'))
        title_label.pack(pady=10)
        
        # Instructions
        instruction_label = ttk.Label(main_frame, text="Select the categories you want to import:", font=('Arial', 9))
        instruction_label.pack(pady=5)
        
        # Create checkboxes for each category
        category_vars = {}
        checkbox_frame = ttk.Frame(main_frame)
        checkbox_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        for category in categories:
            var = tk.BooleanVar(value=True)  # Default to selected
            category_vars[category] = var
            
            checkbox = ttk.Checkbutton(
                checkbox_frame, 
                text=f"📁 {category}", 
                variable=var
            )
            checkbox.pack(anchor=tk.W, pady=2)
        
        # Buttons frame - right after checkboxes
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        selected_categories = []
        
        def select_all():
            for var in category_vars.values():
                var.set(True)
        
        def select_none():
            for var in category_vars.values():
                var.set(False)
        
        def confirm_selection():
            nonlocal selected_categories
            selected_categories = [cat for cat, var in category_vars.items() if var.get()]
            dialog.destroy()
        
        def cancel_selection():
            nonlocal selected_categories
            selected_categories = []
            dialog.destroy()
        
        # Buttons - centered and spaced
        button_inner_frame = ttk.Frame(button_frame)
        button_inner_frame.pack()
        
        # Create buttons
        ttk.Button(button_inner_frame, text="Select All", command=select_all, width=15).pack(side=tk.LEFT, padx=8)
        ttk.Button(button_inner_frame, text="Select None", command=select_none, width=15).pack(side=tk.LEFT, padx=8)
        ttk.Button(button_inner_frame, text="Cancel", command=cancel_selection, width=15).pack(side=tk.LEFT, padx=8)
        ttk.Button(button_inner_frame, text="Import Selected", command=confirm_selection, width=15).pack(side=tk.LEFT, padx=8)
        
        # Auto-resize dialog based on content
        dialog.update_idletasks()
        
        # Calculate required height based on content
        required_height = 200 + (len(categories) * 25) + 100  # Title + categories + buttons + padding
        dialog_width = 650  # Increased width to show full button text
        
        # Center the dialog
        x = (dialog.winfo_screenwidth() // 2) - (dialog_width // 2)
        y = (dialog.winfo_screenheight() // 2) - (required_height // 2)
        dialog.geometry(f"{dialog_width}x{required_height}+{x}+{y}")
        
        # Wait for dialog to close
        dialog.wait_window()
        
        return selected_categories

    def _parse_api_collection(self, collection_data, selected_categories=None):
        """Parse API collection and extract APIs"""
        imported_count = 0
        
        try:
            # Extract collection variables (like baseUrl)
            self.collection_variables = {}
            variables = collection_data.get('variable', [])
            for var in variables:
                if isinstance(var, dict) and 'key' in var and 'value' in var:
                    self.collection_variables[var['key']] = var['value']
            
            if self.collection_variables:
                self.log_message(f"🔧 Found collection variables: {list(self.collection_variables.keys())}")
            
            # Check collection items
            items = collection_data.get('item', [])
            self.log_message(f"🔍 Processing {len(items)} items for import")
            self.log_message(f"📋 Selected categories: {selected_categories}")
            
            for item in items:
                # Folder (category) check
                if item.get('item'):  # This is a folder
                    folder_name = item.get('name', '')
                    
                    # Only process selected categories
                    if selected_categories is None or folder_name in selected_categories:
                        self.log_message(f"📁 Processing folder: {folder_name}")
                        
                        # Check if folder has items
                        folder_items = item.get('item', [])
                        self.log_message(f"   📋 Found {len(folder_items)} items in folder: {folder_name}")
                        
                        if len(folder_items) == 0:
                            self.log_message(f"   ⚠️ No API methods found in folder: {folder_name}")
                        
                        # Process requests in folder (recursive for nested folders)
                        for request_item in folder_items:
                            if self._parse_request_item_recursive(request_item, folder_name):
                                imported_count += 1
                    else:
                        self.log_message(f"⏭️ Skipping folder: {folder_name} (not selected)")
                else:
                    # Single request - only import if no category selection or if "Imported APIs" is selected
                    if selected_categories is None or "Imported APIs" in selected_categories:
                        if self._parse_request_item(item, "Imported APIs"):
                            imported_count += 1
                        
        except Exception as e:
            self.log_message(f"❌ Error parsing collection: {str(e)}")
        
            
        return imported_count
    
    def _find_login_methods(self, collection_data):
        """Find login methods in the collection and add them to dropdown"""
        try:
            self.login_methods = {}
            items = collection_data.get('item', [])
            
            for item in items:
                self._search_login_methods_recursive(item, "")
            
            # Update dropdown
            if self.login_methods:
                login_names = list(self.login_methods.keys())
                self.login_method_combo['values'] = login_names
                if login_names:
                    self.login_method_combo.set(login_names[0])  # Select first one by default
                    self.on_login_method_change()
                self.log_message(f"🔐 Found {len(login_names)} login methods: {', '.join(login_names)}")
            else:
                self.login_method_combo['values'] = ["Default Login"]
                self.login_method_combo.set("Default Login")
                self.log_message("🔐 No login methods found, using default")
                
        except Exception as e:
            self.log_message(f"❌ Error finding login methods: {str(e)}")
    
    def _search_login_methods_recursive(self, item, path):
        """Recursively search for login methods"""
        try:
            if 'request' in item:
                # It's a request
                request_name = item.get('name', '')
                request_data = item['request']
                
                # Check if this looks like a login method
                if self._is_login_method(request_name, request_data):
                    full_name = f"{path}/{request_name}" if path else request_name
                    method = request_data.get('method', 'POST')
                    url_path = request_data.get('url', {}).get('raw', '')
                    
                    # Extract headers
                    headers = {}
                    for header in request_data.get('header', []):
                        if header.get('enabled', True):
                            headers[header.get('key', '')] = header.get('value', '')
                    
                    # Extract body
                    body = '{}'
                    if 'body' in request_data:
                        body_data = request_data['body']
                        if body_data.get('mode') == 'raw':
                            body = body_data.get('raw', '{}')
                    
                    self.login_methods[full_name] = {
                        'name': full_name,
                        'method': method,
                        'url_path': url_path,
                        'headers': headers,
                        'body': body
                    }
            
            elif 'item' in item:
                # It's a folder, search recursively
                folder_name = item.get('name', '')
                new_path = f"{path}/{folder_name}" if path else folder_name
                for sub_item in item['item']:
                    self._search_login_methods_recursive(sub_item, new_path)
                    
        except Exception as e:
            self.log_message(f"❌ Error searching login methods: {str(e)}")
    
    def _is_login_method(self, name, request_data):
        """Check if a request looks like a login method"""
        name_lower = name.lower()
        login_keywords = ['login', 'auth', 'authenticate', 'signin', 'sign-in', 'token', 'session']
        
        # Check name
        if any(keyword in name_lower for keyword in login_keywords):
            return True
        
        # Check URL
        url = request_data.get('url', {})
        if isinstance(url, dict):
            url_str = url.get('raw', '').lower()
            if any(keyword in url_str for keyword in login_keywords):
                return True
        
        return False
    
    def _parse_request_item_recursive(self, request_item, category_name, subcategory_name=None):
        """Parse request item recursively (handles nested folders)"""
        try:
            # Check if it's a request (has 'request' key)
            if 'request' in request_item:
                # Use the correct category structure
                if subcategory_name:
                    full_category_key = f"{category_name}|{subcategory_name}"
                else:
                    full_category_key = category_name
                return self._parse_request_item(request_item, full_category_key)
            
            # Check if it's a nested folder (has 'item' key)
            elif 'item' in request_item:
                subfolder_name = request_item.get('name', 'Unknown')
                self.log_message(f"    📂 Processing subfolder: {subfolder_name}")
                
                subfolder_items = request_item.get('item', [])
                self.log_message(f"      📋 Found {len(subfolder_items)} items in subfolder: {subfolder_name}")
                
                imported_count = 0
                for sub_item in subfolder_items:
                    # Pass the subfolder name as the subcategory for nested items
                    if self._parse_request_item_recursive(sub_item, category_name, subfolder_name):
                        imported_count += 1
                
                if imported_count == 0:
                    self.log_message(f"      ⚠️ No API methods found in subfolder: {subfolder_name}")
                else:
                    self.log_message(f"      ✅ Imported {imported_count} methods from subfolder: {subfolder_name}")
                
                return imported_count > 0
                
        except Exception as e:
            self.log_message(f"  ❌ Error parsing item recursively: {str(e)}")
            
        return False

    def _parse_request_item(self, request_item, category_name):
        """Parse single request item"""
        try:
            request_name = request_item.get('name', '')
            request_data = request_item.get('request', {})
            
            if not request_data:
                return False
            
            # Method and URL
            method = request_data.get('method', 'GET')
            url_data = request_data.get('url', {})
            
            # Build URL path and clean Postman variables
            if isinstance(url_data, str):
                full_url = url_data
            else:
                full_url = url_data.get('raw', '') or url_data.get('path', '')
                if isinstance(full_url, list):
                    full_url = '/' + '/'.join(full_url)
            
            # Clean Postman variables from the URL
            cleaned_url = self._clean_postman_variables(full_url)
            
            # Extract base URL and path
            if '://' in cleaned_url:
                # It's a full URL, extract base URL and path
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(cleaned_url)
                    base_url = f"{parsed.scheme}://{parsed.netloc}"
                    path = parsed.path if parsed.path else "/"
                except:
                    # Fallback: simple string manipulation
                    parts = cleaned_url.split('/', 3)
                    if len(parts) >= 3:
                        base_url = f"{parts[0]}//{parts[2]}"
                        path = '/' + parts[3] if len(parts) > 3 else "/"
                    else:
                        base_url = "https://api.example.com"
                        path = "/"
            else:
                # It's just a path
                base_url = "https://api.example.com"
                path = cleaned_url if cleaned_url.startswith('/') else '/' + cleaned_url
            
            # Headers
            headers = {}
            for header in request_data.get('header', []):
                if header.get('enabled', True):
                    headers[header.get('key', '')] = header.get('value', '')
            
            # Body
            body = ""
            body_data = request_data.get('body', {})
            if body_data:
                if body_data.get('mode') == 'raw':
                    body = body_data.get('raw', '')
                elif body_data.get('mode') == 'formdata':
                    # Convert form data to JSON
                    form_data = {}
                    for form_item in body_data.get('formdata', []):
                        if form_item.get('enabled', True):
                            form_data[form_item.get('key', '')] = form_item.get('value', '')
                    body = json.dumps(form_data, indent=2)
            
            # Query parameters
            params = {}
            for param in request_data.get('url', {}).get('query', []):
                if param.get('enabled', True):
                    params[param.get('key', '')] = param.get('value', '')
            
            # Add to imported APIs (preserve duplicates by uniquifying the name)
            if category_name not in self.imported_apis:
                self.imported_apis[category_name] = {}
            
            unique_name = request_name
            if unique_name in self.imported_apis[category_name]:
                counter = 2
                while f"{request_name} ({counter})" in self.imported_apis[category_name]:
                    counter += 1
                unique_name = f"{request_name} ({counter})"
            
            self.imported_apis[category_name][unique_name] = {
                "method": method,
                "base_url": base_url,
                "path": path,
                "headers": headers,
                "body": body,
                "params": params
            }
            
            self.log_message(f"  ✅ Imported: {unique_name} ({method} {base_url}{path})")
            return True
            
        except Exception as e:
            self.log_message(f"  ❌ Error parsing request: {str(e)}")
            return False
    
    def _update_category_list(self):
        """Update category list with subcategories (initially collapsed)"""
        # Clear existing categories
        self.category_listbox.delete(0, tk.END)
        
        if self.imported_apis:
            # Group APIs by category and subcategory
            category_structure = {}
            for category_key in self.imported_apis.keys():
                methods = self.imported_apis[category_key]
                
                # Parse category key (format: "MainCategory|SubCategory" or just "MainCategory")
                if '|' in category_key:
                    main_category, subcategory = category_key.split('|', 1)
                else:
                    main_category = category_key
                    subcategory = "Main"  # Use "Main" instead of "General" for top-level categories
                
                # Initialize main category if not exists
                if main_category not in category_structure:
                    category_structure[main_category] = {}
                
                # Initialize subcategory if not exists
                if subcategory not in category_structure[main_category]:
                    category_structure[main_category][subcategory] = []
                
                # Add all methods (including duplicates with suffixes) to the subcategory preserving order
                for method_name in methods.keys():
                    category_structure[main_category][subcategory].append(method_name)
                
            
            # Store category structure for later use
            self.category_structure = category_structure
            
            # Display only main categories (subcategories collapsed initially)
            for category in sorted(category_structure.keys()):
                total_methods = sum(len(methods) for methods in category_structure[category].values())
                self.category_listbox.insert(tk.END, f"📁 {category} ({total_methods} methods)")
            
            self.log_message(f"📋 Updated category list with {len(category_structure)} categories (subcategories collapsed)")
        else:
            # No collection imported - show message
            self.category_listbox.insert(tk.END, "⚠️ No collection imported")
            self.log_message("⚠️ Please import an API collection first")
    
    def _clean_postman_variables(self, url_or_path):
        """Replace Postman variables with actual values from collection variables"""
        if not url_or_path:
            return ""
        
        import re
        
        # Replace collection variables with their values
        cleaned = url_or_path
        for var_name, var_value in self.collection_variables.items():
            pattern = r'\{\{' + re.escape(var_name) + r'\}\}'
            cleaned = re.sub(pattern, var_value, cleaned)
        
        # Remove any remaining unresolved variables
        cleaned = re.sub(r'\{\{[^}]+\}\}', '', cleaned)
        
        # Fix protocol issues - ensure https:// or http:// is properly formatted
        cleaned = re.sub(r'https?:/+', 'https://', cleaned)
        
        # Clean up any double slashes that might result from variable removal, but preserve protocol
        # Split by protocol first to avoid breaking https://
        if '://' in cleaned:
            protocol, rest = cleaned.split('://', 1)
            # Clean up multiple slashes in the rest part
            rest = re.sub(r'/+', '/', rest)
            cleaned = f"{protocol}://{rest}"
        else:
            # If no protocol, just clean up multiple slashes
            cleaned = re.sub(r'/+', '/', cleaned)
        
        return cleaned.strip()
    
    def _add_auth_headers(self, headers, context=""):
        """Add authentication headers (Bearer token, XSRF token) to request headers"""
        # Add Bearer token if available and not already present
        if self.auth_token and not headers.get("Authorization"):
            headers["Authorization"] = f"Bearer {self.auth_token}"
            self.log_message(f"🔐 Added Bearer Token to {context}: {self.auth_token[:20]}...")
        
        # Add XSRF token if available and not already present
        if self.xsrf_token and (not headers.get("X-XSRF-TOKEN") or headers.get("X-XSRF-TOKEN") == "{{xsrf_token}}" or headers.get("X-XSRF-TOKEN") == ""):
            headers["X-XSRF-TOKEN"] = self.xsrf_token
            self.log_message(f"🔐 Added XSRF Token to {context}: {self.xsrf_token[:20]}...")
        
        # Log if no tokens available
        if not self.auth_token and not self.xsrf_token:
            self.log_message(f"⚠️ No authentication tokens available for {context}")
    
    def _extract_auth_tokens(self, response):
        """Extract authentication tokens from response (XSRF, Bearer, etc.)"""
        # Extract Bearer token from response body (for login responses)
        try:
            if response.text:
                response_json = response.json()
                if 'token' in response_json:
                    new_auth_token = response_json['token']
                    if new_auth_token and new_auth_token != self.auth_token:
                        self.auth_token = new_auth_token
                        self.log_message(f"🔐 Auth Token extracted from response: {self.auth_token[:20]}...")
        except:
            pass
        
        # Extract XSRF token from headers
        if 'XSRF-TOKEN' in response.headers:
            new_xsrf_token = response.headers['XSRF-TOKEN']
            if new_xsrf_token and new_xsrf_token != self.xsrf_token:
                self.xsrf_token = new_xsrf_token
                self.log_message(f"🔐 XSRF Token updated from header: {self.xsrf_token[:20]}...")
        
        # Extract XSRF token from cookies
        if hasattr(response, 'cookies') and 'XSRF-TOKEN' in response.cookies:
            new_xsrf_cookie = response.cookies.get('XSRF-TOKEN')
            if new_xsrf_cookie and new_xsrf_cookie != self.xsrf_token:
                self.xsrf_token = new_xsrf_cookie
                self.log_message(f"🔐 XSRF Token updated from cookie: {self.xsrf_token[:20]}...")
        
        # Extract XSRF token from Set-Cookie header
        if 'Set-Cookie' in response.headers:
            set_cookie = response.headers['Set-Cookie']
            if 'XSRF-TOKEN=' in set_cookie:
                import re
                match = re.search(r'XSRF-TOKEN=([^;]+)', set_cookie)
                if match:
                    new_xsrf_token = match.group(1)
                    if new_xsrf_token and new_xsrf_token != self.xsrf_token:
                        self.xsrf_token = new_xsrf_token
                        self.log_message(f"🔐 XSRF Token extracted from Set-Cookie: {self.xsrf_token[:20]}...")
        
        # Debug: Show current token status
        if self.auth_token:
            self.log_message(f"🔐 Current Auth Token: {self.auth_token[:20]}...")
        if self.xsrf_token:
            self.log_message(f"🔐 Current XSRF Token: {self.xsrf_token[:20]}...")
        if not self.auth_token and not self.xsrf_token:
            self.log_message("⚠️ No authentication tokens available")
    
    def _is_valid_url(self, url):
        """Validate URL format"""
        if not url:
            return False
        
        # Check for basic URL format
        if not ('://' in url):
            return False
        
        # Check for proper protocol
        if not url.startswith(('http://', 'https://')):
            return False
        
        # Check for host part
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return bool(parsed.netloc)  # netloc should not be empty
        except:
            return False
    
    def _extract_path_from_url(self, url_or_path):
        """Extract only the path portion from a URL or return the path as is"""
        if not url_or_path:
            return "/"
        
        # First clean Postman variables
        cleaned_url = self._clean_postman_variables(url_or_path)
        
        # If it's already just a path (starts with /), return as is
        if cleaned_url.startswith('/'):
            return cleaned_url
        
        # If it's a full URL, extract the path part
        if '://' in cleaned_url:
            try:
                from urllib.parse import urlparse
                parsed = urlparse(cleaned_url)
                path = parsed.path
                # If path is empty, return "/"
                return path if path else "/"
            except:
                # If parsing fails, try simple string manipulation
                if '/' in cleaned_url:
                    # Find the path part after the domain
                    parts = cleaned_url.split('/', 3)  # Split into max 4 parts
                    if len(parts) >= 4:
                        return '/' + parts[3]  # Return everything after domain
                    else:
                        return "/"
                else:
                    return "/"
        
        # If it doesn't start with / and doesn't contain ://, assume it's a path and add /
        return '/' + cleaned_url.lstrip('/')
    
    
    def _update_field_visibility(self, api_info):
        """Show/hide fields based on method type"""
        method = api_info.get("method", "GET")
        has_body = api_info.get("body", "") != ""
        has_params = api_info.get("params", {}) != {}
        
        # Show/hide body field
        if has_body or method in ["POST", "PUT"]:
            # Show body field
            self.body_label.grid()
            self.body_text.grid()
            self.save_body_button.grid()
            self.log_message(f"📄 Request Body field shown (Method: {method})")
        else:
            # Hide body field
            self.body_label.grid_remove()
            self.body_text.grid_remove()
            self.save_body_button.grid_remove()
            self.log_message(f"📄 Request Body field hidden (Method: {method})")
        
        # Show/hide parameters field
        if has_params or method == "GET":
            # Show parameters field
            self.params_label.grid()
            self.params_text.grid()
            self.save_params_button.grid()
            self.log_message(f"🔍 Query Parameters field shown (Method: {method})")
        else:
            # Hide parameters field
            self.params_label.grid_remove()
            self.params_text.grid_remove()
            self.save_params_button.grid_remove()
            self.log_message(f"🔍 Query Parameters field hidden (Method: {method})")
    
    def _update_dynamic_template(self):
        """Save current form values as dynamic template - prioritize saved values"""
        if not self.selected_category or not self.selected_method:
            return
        
        method_key = f"{self.selected_category} - {self.selected_method}"
        
        # Use saved values first, otherwise use current form values
        headers_text = self.saved_headers.get(method_key, self.headers_text.get("1.0", tk.END).strip())
        base_url = self.saved_urls.get(method_key, self.base_url_entry.get().strip())
        path = self.saved_paths.get(method_key, self.path_entry.get().strip())
        
        # Parse and clean headers
        try:
            headers = json.loads(headers_text) if headers_text else {}
        except:
            headers = {}
        
        # Clean Postman variables from headers
        cleaned_headers = {}
        for key, value in headers.items():
            if isinstance(value, str):
                cleaned_value = self._clean_postman_variables(value)
                cleaned_headers[key] = cleaned_value
            else:
                cleaned_headers[key] = value
        
        headers = cleaned_headers
        
        # Ensure XSRF token is properly set
        if self.xsrf_token and (not headers.get("X-XSRF-TOKEN") or headers.get("X-XSRF-TOKEN") == "{{xsrf_token}}" or headers.get("X-XSRF-TOKEN") == ""):
            headers["X-XSRF-TOKEN"] = self.xsrf_token
        
        # For body - use empty string if field is hidden
        if self.body_text.winfo_viewable():
            body = self.saved_bodies.get(method_key, self.body_text.get("1.0", tk.END).strip())
        else:
            body = self.saved_bodies.get(method_key, "")
        
        # For params - use empty string if field is hidden
        if self.params_text.winfo_viewable():
            params = self.saved_params.get(method_key, self.params_text.get("1.0", tk.END).strip())
        else:
            params = self.saved_params.get(method_key, "")
        
        current_template = {
            "method": self.method_combo.get(),
            "base_url": base_url,
            "path": path,
            "headers": headers,
            "body": body,
            "params": params
        }
        
        # Update dynamic template
        self.dynamic_templates[method_key] = current_template
        self.log_message(f"🔄 Dynamic template updated for: {self.selected_method}")
        
        # Log saved values if they exist
        saved_items = []
        if method_key in self.saved_headers:
            saved_items.append("Headers")
        if method_key in self.saved_bodies:
            saved_items.append("Body")
        if method_key in self.saved_params:
            saved_items.append("Params")
        if method_key in self.saved_urls:
            saved_items.append("URL")
        if method_key in self.saved_paths:
            saved_items.append("Path")
        
        if saved_items:
            self.log_message(f"💾 Using saved values for: {', '.join(saved_items)}")
    
    def save_headers(self):
        """Save headers"""
        if not self.selected_category or not self.selected_method:
            messagebox.showwarning("Warning", "Please select a method first!")
            return
        
        method_key = f"{self.selected_category} - {self.selected_method}"
        headers_content = self.headers_text.get("1.0", tk.END).strip()
        
        self.saved_headers[method_key] = headers_content
        self.log_message(f"💾 Headers saved for: {self.selected_method}")
        
        # Make save button green
        self.save_headers_button.config(text="✅ Headers Saved")
        self.root.after(2000, lambda: self.save_headers_button.config(text="💾 Save Headers"))
    
    def save_body(self):
        """Save request body"""
        if not self.selected_category or not self.selected_method:
            messagebox.showwarning("Warning", "Please select a method first!")
            return
        
        method_key = f"{self.selected_category} - {self.selected_method}"
        body_content = self.body_text.get("1.0", tk.END).strip()
        
        self.saved_bodies[method_key] = body_content
        self.log_message(f"💾 Request Body saved for: {self.selected_method}")
        
        # Make save button green
        self.save_body_button.config(text="✅ Body Saved")
        self.root.after(2000, lambda: self.save_body_button.config(text="💾 Save Body"))
    
    def save_params(self):
        """Save query parameters"""
        if not self.selected_category or not self.selected_method:
            messagebox.showwarning("Warning", "Please select a method first!")
            return
        
        method_key = f"{self.selected_category} - {self.selected_method}"
        params_content = self.params_text.get("1.0", tk.END).strip()
        
        self.saved_params[method_key] = params_content
        self.log_message(f"💾 Query Parameters saved for: {self.selected_method}")
        
        # Make save button green
        self.save_params_button.config(text="✅ Parameters Saved")
        self.root.after(2000, lambda: self.save_params_button.config(text="💾 Save Parameters"))
    
    def save_url(self):
        """Save base URL"""
        if not self.selected_category or not self.selected_method:
            messagebox.showwarning("Warning", "Please select a method first!")
            return
        
        method_key = f"{self.selected_category} - {self.selected_method}"
        url_content = self.base_url_entry.get().strip()
        
        self.saved_urls[method_key] = url_content
        self.log_message(f"💾 Base URL saved for: {self.selected_method}")
        
        # Make save button green
        self.save_url_button.config(text="✅ URL Saved")
        self.root.after(2000, lambda: self.save_url_button.config(text="💾 Save URL"))
    
    def save_path(self):
        """Save path"""
        if not self.selected_category or not self.selected_method:
            messagebox.showwarning("Warning", "Please select a method first!")
            return
        
        method_key = f"{self.selected_category} - {self.selected_method}"
        path_content = self.path_entry.get().strip()
        
        self.saved_paths[method_key] = path_content
        self.log_message(f"💾 Path saved for: {self.selected_method}")
        
        # Make save button green
        self.save_path_button.config(text="✅ Path Saved")
        self.root.after(2000, lambda: self.save_path_button.config(text="💾 Save Path"))
    
    def add_to_order(self):
        """Add selected method to automation order"""
        if not self.selected_category or not self.selected_method:
            messagebox.showwarning("Warning", "Please select a method first!")
            return
        
        method_name = f"{self.selected_category} - {self.selected_method}"
        if method_name not in self.automation_methods:
            # First save current form values as dynamic template
            self._update_dynamic_template()
            
            self.automation_methods.append(method_name)
            # Add without icon (icon will be added after execution)
            self.method_order_listbox.insert(tk.END, method_name)
            self.log_message(f"✓ Added to automation: {method_name}")
            self.log_message(f"💾 Current form values saved as dynamic template")
        else:
            messagebox.showinfo("Info", "Method already in automation list!")
    
    def remove_from_order(self):
        """Remove selected method from automation order"""
        selection = self.method_order_listbox.curselection()
        if selection:
            index = selection[0]
            method_name = self.method_order_listbox.get(index)
            self.method_order_listbox.delete(index)
            # Remove from automation_methods list
            if method_name in self.automation_methods:
                self.automation_methods.remove(method_name)
            self.log_message(f"✓ Removed from automation: {method_name}")
        else:
            messagebox.showwarning("Warning", "Please select a method to remove!")
    
    def move_method_up(self):
        """Move selected method up"""
        selection = self.method_order_listbox.curselection()
        if selection and selection[0] > 0:
            index = selection[0]
            method_name = self.method_order_listbox.get(index)
            
            # Remove from listbox and add to new position
            self.method_order_listbox.delete(index)
            self.method_order_listbox.insert(index - 1, method_name)
            self.method_order_listbox.selection_set(index - 1)
            
            # Move in list as well
            self.automation_methods.insert(index - 1, self.automation_methods.pop(index))
    
    def move_method_down(self):
        """Move selected method down"""
        selection = self.method_order_listbox.curselection()
        if selection and selection[0] < len(self.automation_methods) - 1:
            index = selection[0]
            method_name = self.method_order_listbox.get(index)
            
            # Remove from listbox and add to new position
            self.method_order_listbox.delete(index)
            self.method_order_listbox.insert(index + 1, method_name)
            self.method_order_listbox.selection_set(index + 1)
            
            # Move in list as well
            self.automation_methods.insert(index + 1, self.automation_methods.pop(index))
    
    def run_automation(self):
        """Start automation"""
        if not self.automation_methods:
            messagebox.showwarning("Warning", "Please add methods to automation list first!")
            return
        
        # Clear previous results
        self.automation_results = {}
        # Create a fresh queue copy so original order remains for subsequent runs
        self._automation_queue = list(self.automation_methods)
        
        # Clear icons in listbox
        for i in range(self.method_order_listbox.size()):
            current_text = self.method_order_listbox.get(i)
            if current_text.startswith("✅") or current_text.startswith("❌"):
                # Remove icon
                method_name = current_text[2:].strip()  # Remove icon
                self.method_order_listbox.delete(i)
                self.method_order_listbox.insert(i, method_name)
        
        self.automation_running = True
        self.run_automation_button.config(state=tk.DISABLED)
        self.stop_automation_button.config(state=tk.NORMAL)
        self.automation_status_label.config(text="Running...", foreground="green")
        
        self.log_message("🚀 Starting automation...")
        self.root.after(1000, self._run_next_automation_method)
    
    def stop_automation(self):
        """Stop automation"""
        self.automation_running = False
        self.run_automation_button.config(state=tk.NORMAL)
        self.stop_automation_button.config(state=tk.DISABLED)
        self.automation_status_label.config(text="Stopped", foreground="red")
        self.log_message("⏹️ Automation stopped by user")
    
    def _run_next_automation_method(self):
        """Run next automation method"""
        if not self.automation_running or not self._automation_queue:
            self._finish_automation()
            return
        
        method_name = self._automation_queue.pop(0)
        
        # Split category and method from method name
        try:
            category, method = method_name.split(" - ", 1)
            self.log_message(f"🔄 Running: {method_name}")
            self.automation_status_label.config(text=f"Running: {method}")
            
            # Use dynamic template if available, otherwise use original API info
            if method_name in self.dynamic_templates:
                self.log_message(f"💾 Using dynamic template for: {method}")
                success = self.execute_api_test_with_template(category, method, method_name)
            else:
                self.log_message(f"📋 Using original template for: {method}")
                success = self.execute_api_test(category, method)
            
            # Save result
            self.automation_results[method_name] = success
            
            # Update method in listbox (with icon)
            self._update_method_status(method_name, success)
            
            # Wait 2 seconds and move to next
            self.root.after(2000, self._run_next_automation_method)
            
        except Exception as e:
            self.log_message(f"❌ Error in automation: {str(e)}")
            self.automation_results[method_name] = False
            self._update_method_status(method_name, False)
            self.root.after(1000, self._run_next_automation_method)
    
    def _update_method_status(self, method_name, success):
        """Update method status in listbox"""
        # Find and update method in listbox
        for i in range(self.method_order_listbox.size()):
            current_text = self.method_order_listbox.get(i)
            # Check text with or without icon
            if current_text == method_name or current_text.endswith(method_name):
                # Add icon
                icon = "✅" if success else "❌"
                updated_text = f"{icon} {method_name}"
                self.method_order_listbox.delete(i)
                self.method_order_listbox.insert(i, updated_text)
                break
    
    def _finish_automation(self):
        """Finish automation"""
        self.automation_running = False
        self.run_automation_button.config(state=tk.NORMAL)
        self.stop_automation_button.config(state=tk.DISABLED)
        self.automation_status_label.config(text="Completed", foreground="blue")
        
        # Summarize results
        total_methods = len(self.automation_results)
        successful_methods = sum(1 for success in self.automation_results.values() if success)
        failed_methods = total_methods - successful_methods
        
        self.log_message("✅ Automation completed!")
        self.log_message(f"📊 Results: {successful_methods} successful, {failed_methods} failed out of {total_methods} total")
    
    def clear_results(self):
        """Clear results"""
        self.result_text.delete("1.0", tk.END)
    
    def export_results(self):
        """Export results to file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.result_text.get("1.0", tk.END))
                messagebox.showinfo("Success", f"Results exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def copy_results(self):
        """Copy results to clipboard"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.result_text.get("1.0", tk.END))
            messagebox.showinfo("Success", "Results copied to clipboard")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = APITestAutomationTool(root)
    root.mainloop()

