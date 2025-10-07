# API Test Automation Tool

A zero-config, GUI-based API runner for Postman collections. Import a collection, pick endpoints, and run single requests or full automations with dynamic data and XSRF handling.

<img width="1917" height="1048" alt="image" src="https://github.com/user-attachments/assets/dd29e15f-fdcf-4156-9de8-37868ba8bd1f" />


## Quick start

Requirements:
- Python 3.8+
- Windows, macOS, or Linux

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the app:
```bash
python api_automation_tool.py
```

## What you can do

- Import a Postman collection and browse categories/subcategories
- Load a method’s request as an editable template (headers, body, params)
- Send one-off requests from the builder
- Queue multiple methods and Run Automation (re-usable between runs)
- Store and auto-apply XSRF tokens across requests
- Export logs, copy results, and save per-field edits

## Using the UI

1) Import Collection
- Click “Import”, select a Postman collection JSON
- All folders and requests are parsed; duplicates are preserved (e.g., “Login (2)”) 
- “Remove” clears the imported collection and UI state

2) Select and Load Methods
- Choose a category on the left; methods appear below
- Click a method, then “Load Template” to populate the builder

3) Build and Send Requests
- Method: GET/POST/PUT/DELETE
- URL: uses Base URL + Path (never paste a full URL into Path)
- Headers/Body are JSON format; Query Parameters are URL-encoded format (param1=value1&param2=value2); click Save to persist each field
- Send Request to execute immediately

4) Automation
- Click Add to queue the currently loaded method (with your saved edits)
- Reorder with ↑/↓; Remove to unqueue
- Run Automation executes top-to-bottom and can be re-run without rebuilding the list

## Authentication handling

- **Bearer Tokens**: Automatically extracted from login responses and added to all requests
- **XSRF Tokens**: Extracted from response headers, cookies, or Set-Cookie
- **Smart Headers**: If a header contains `{{xsrf_token}}` or `{{authToken}}`, it is replaced automatically
- **Tip**: Place a login/auth step first in Automation so protected endpoints succeed

## Working with collections

Supported Postman features:
- Folders and nested folders (rendered as categories and subcategories)
- Request name, method, URL, headers, body (raw/form-data), query params
- Duplicate names preserved by suffixing: “Name (2)”, “Name (3)”, …

Cleaning Postman variables:
- Variables like `{{baseUrl}}`, `{{url}}`, etc. are removed from URLs
- Paths are normalized so exported and built URLs are valid

## Exporting results

- Use “Export” in Results to save a full, timestamped log
- “Copy” places the log onto the clipboard

## Tips

- Use Base URL for the host and scheme; put only the endpoint path in Path
- For DELETE: both Body and Params are supported
- Each request has a 30s timeout; SSL verification is disabled for convenience

## Troubleshooting

- Missing or invalid XSRF token (403)
  - Ensure a login/auth request runs before protected endpoints
  - Confirm the server issues `XSRF-TOKEN` in headers/cookies
- Path builds a wrong URL
  - Keep only `/rest/...` in Path; put `https://host` in Base URL
- Duplicate methods not visible
  - Ensure you selected the parent category; the tool lists all nested methods and preserves duplicates with numeric suffixes

## Contributing

Contributions are welcome. Typical areas:
- Parser improvements for more Postman formats
- Additional auth flows (OAuth2, JWT helpers)
- Better export/report formats

Please open an issue describing the change before submitting a PR.

## License

This tool is provided as-is for general API testing and automation. Use at your own risk.
