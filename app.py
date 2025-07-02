import cloudscraper
from quart import Quart, Response, request

# --- Settings ---
TARGET_BASE_URL = "https://tryveo3.ai"
# -----------------

app = Quart(__name__)

# Create a single, reusable scraper instance
scraper = cloudscraper.create_scraper()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
async def proxy(path):
    """
    Handles proxying requests using the lightweight cloudscraper library.
    This is much more efficient and stable than a full browser.
    """
    
    target_url = f"{TARGET_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    if request.query_string:
        target_url += "?" + request.query_string.decode('utf-8')

    print(f"--- New Request ---")
    print(f"INFO: Proxying with cloudscraper to: {target_url}")

    try:
        # Use a standard synchronous get request inside a thread managed by Quart
        # This is the recommended way for I/O-bound tasks in Quart.
        response = await app.sync_to_async(scraper.get)(target_url)
        
        # Check if the request was successful
        response.raise_for_status()
        
        print(f"SUCCESS: Got {response.status_code} from target.")

        # Extract headers. We need to be careful here.
        # We only forward the content-type.
        content_type = response.headers.get('Content-Type', 'text/html')
        
        return Response(response.text, status=response.status_code, mimetype=content_type)

    except Exception as e:
        print(f"FATAL: An error occurred: {e}")
        return f"An error occurred while trying to proxy the request: {e}", 500
