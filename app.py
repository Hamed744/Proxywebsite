import asyncio
from quart import Quart, Response, request
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# --- Settings ---
TARGET_BASE_URL = "https://tryveo3.ai"
# -----------------

app = Quart(__name__)

# A global variable to hold the single browser instance
browser_instance = None
# A lock to ensure only one request is processed at a time, preventing race conditions.
request_lock = asyncio.Lock()

@app.before_serving
async def startup():
    """This function runs once when the application starts."""
    global browser_instance
    print("INFO: Launching a single, shared browser instance...")
    p = await async_playwright().start()
    browser_instance = await p.chromium.launch(
        headless=True,
        args=[
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu'
        ]
    )
    print("SUCCESS: Shared browser has been launched and is ready.")

@app.after_serving
async def shutdown():
    """This function runs once when the application stops."""
    if browser_instance:
        await browser_instance.close()
        print("SUCCESS: Shared browser has been shut down.")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
async def proxy(path):
    """Handles proxying requests serially to prevent race conditions."""
    if browser_instance is None:
        return "Error: Browser is not ready, please try again in a moment.", 503

    target_url = f"{TARGET_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    if request.query_string:
        target_url += "?" + request.query_string.decode('utf-8')

    print(f"--- New Request ---")
    print(f"INFO: Waiting for lock to proxy: {target_url}")

    # This lock ensures that only one request can be in this block at a time.
    async with request_lock:
        print(f"INFO: Lock acquired. Processing: {target_url}")
        context = None
        try:
            context = await browser_instance.new_context(
                 user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            print("INFO: Navigating...")
            await page.goto(target_url, timeout=120000, wait_until="domcontentloaded")
            print("INFO: Page navigation complete. Getting content...")
            
            content = await page.content()
            print("SUCCESS: Content retrieved.")
            
            # The response is prepared here but returned after the finally block.
            response = Response(content, status=200, mimetype="text/html")
            
        except PlaywrightTimeoutError:
            print(f"ERROR: Timeout (120s) occurred for {target_url}")
            response = Response("Error: The request to the target site timed out.", status=504, mimetype="text/plain")
        except Exception as e:
            print(f"FATAL: An unexpected error occurred: {e}")
            response = Response("An internal server error occurred in the proxy.", status=500, mimetype="text/plain")
        finally:
            if context:
                await context.close()
                print("INFO: Browser context closed.")
        
        print("INFO: Lock released.")
        return response
