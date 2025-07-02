import os
import asyncio
from flask import Flask, Response, request
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import atexit

TARGET_BASE_URL = "https://tryveo3.ai"
app = Flask(__name__)

# The state dictionary. All items will be created lazily.
browser_instance = {
    "browser": None,
    "context": None,
    "lock": None,
}

# Use a standard threading lock to protect the lazy initialization of asyncio objects
# This is safe to share across threads.
_init_lock = asyncio.Lock()

async def get_browser_context():
    """
    Lazily initializes the Playwright browser and its context in a thread-safe
    and event-loop-safe manner.
    """
    # Use the async lock to ensure only one coroutine initializes the browser.
    async with _init_lock:
        if browser_instance["context"] is None:
            print("INFO: First-time setup. Launching Playwright browser...")
            p = await async_playwright().start()
            
            launch_args = [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu'
            ]
            
            browser_instance["browser"] = await p.chromium.launch(headless=True, args=launch_args)
            browser_instance["context"] = await browser_instance["browser"].new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
            )
            print("SUCCESS: Playwright browser has been launched.")
    return browser_instance["context"]


async def shutdown_playwright():
    """Gracefully closes the browser on application exit."""
    print("INFO: Attempting to shut down Playwright...")
    if browser_instance["context"]:
        await browser_instance["context"].close()
    if browser_instance["browser"]:
        await browser_instance["browser"].close()
    print("SUCCESS: Playwright has been shut down.")


@atexit.register
def cleanup():
    """Ensures shutdown_playwright is called when the app exits."""
    try:
        # Try to get the running event loop.
        loop = asyncio.get_running_loop()
        if loop.is_running():
            loop.create_task(shutdown_playwright())
        else: # If no loop is running, run it in a new one.
            asyncio.run(shutdown_playwright())
    except RuntimeError: # This happens if there's no running loop.
        asyncio.run(shutdown_playwright())


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
async def proxy(path):
    page = None
    try:
        print("INFO: Request received. Acquiring browser context...")
        context = await get_browser_context()
        print("INFO: Browser context acquired.")
    except Exception as e:
        print(f"FATAL: Failed to initialize browser: {e}")
        return "Error: Failed to initialize the proxy browser.", 503

    target_url = f"{TARGET_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    if request.query_string:
        target_url += "?" + request.query_string.decode('utf-8')
    
    print(f"INFO: Proxying to: {target_url}")

    try:
        page = await context.new_page()
        print("INFO: New page created. Navigating...")
        
        await page.goto(target_url, timeout=90000, wait_until="domcontentloaded")
        print("INFO: Page navigation complete. Getting content...")
        
        content = await page.content()
        print("SUCCESS: Content retrieved.")
        
        return Response(content, status=200, mimetype="text/html")

    except PlaywrightTimeoutError:
        print(f"ERROR: Timeout (90s) occurred for {target_url}")
        return "Error: The request to the target site timed out.", 504
    except Exception as e:
        print(f"ERROR: An unexpected error occurred during proxying: {e}")
        return f"An internal server error occurred in the proxy.", 500
    finally:
        if page:
            await page.close()
            print("INFO: Page closed to release resources.")
