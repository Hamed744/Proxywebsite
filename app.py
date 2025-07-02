import cloudscraper
from flask import Flask, Response, request

# --- Settings ---
TARGET_BASE_URL = "https://hamed744-veu3.static.hf.space"
# -----------------

app = Flask(__name__)

# Create a single, reusable scraper instance
scraper = cloudscraper.create_scraper()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    """
    Handles proxying requests using the lightweight cloudscraper library
    with the simple and robust Flask framework.
    """
    
    target_url = f"{TARGET_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    if request.query_string:
        target_url += "?" + request.query_string.decode('utf-8')

    print(f"--- New Request ---")
    print(f"INFO: Proxying with cloudscraper to: {target_url}")

    try:
        response = scraper.get(target_url, timeout=30) # 30 second timeout
        
        # Check if the request was successful
        response.raise_for_status()
        
        print(f"SUCCESS: Got {response.status_code} from target.")

        content_type = response.headers.get('Content-Type', 'text/html')
        
        return Response(response.text, status=response.status_code, mimetype=content_type)

    except Exception as e:
        print(f"FATAL: An error occurred: {e}")
        return f"An error occurred while trying to proxy the request: {e}", 500
