import asyncio
from quart import Quart, Response, request
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# --- Settings ---
TARGET_BASE_URL = "https://tryveo3.ai"
# -----------------

app = Quart(__name__)

# A global variable to hold the single browser instance
browser_instance = None
browser_lock = asyncio.Lock()

@app.before_serving
async def startup():
    """This function runs once when the application starts."""
    global browser_instance
    async with browser_lock:
        if browser_instance is None:
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
    global browser_instance
    if browser_instance:
        await browser_instance.close()
        print("SUCCESS: Shared browser has been shut down.")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
async def proxy(path):
    """Handles proxying requests using the shared browser instance."""
    if browser_instance is None:
        return "Error: Browser is not ready, please try again in a moment.", 503

    target_url = f"{TARGET_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    if request.query_string:
        target_url += "?" + request.query_string.decode('utf-8')

    print(f"--- New Request ---")
    print(f"INFO: Proxying to: {target_url}")

    context = None
    # Variables to hold the result
    response_content = "An internal error occurred."
    response_status = 500
    
    try:
        # Create a new, isolated context for each request.
        context = await browser_instance.new_context(
             user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print("INFO: Navigating...")
        # Use a longer timeout just in case
        await page.goto(target_url, timeout=120000, wait_until="domcontentloaded")
        print("INFO: Page navigation complete. Getting content...")
        
        # Store the content and status for later use
        response_content = await page.content()
        response_status = 200
        print("SUCCESS: Content retrieved.")
        
    except PlaywrightTimeoutError:
        print(f"ERROR: Timeout (120s) occurred for {target_url}")
        response_content = "Error: The request to the target site timed out."
        response_status = 504
    except Exception as e:
        print(f"FATAL: An unexpected error occurred: {e}")
        response_content = "An internal server error occurred in the proxy."
        response_status = 500
    finally:
        # This block ALWAYS runs, ensuring the context is closed.
        if context:
            await context.close()
            print("INFO: Browser context closed to release resources.")
            
    # Return the response AFTER all playwright operations are complete and closed.
    return Response(response_content, status=response_status, mimetype="text/html")
