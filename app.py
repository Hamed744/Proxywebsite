import asyncio
from flask import Flask, Response, request
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# هیچ متغیر سراسری برای مرورگر وجود ندارد. همه چیز داخل خود تابع است.

TARGET_BASE_URL = "https://tryveo3.ai"
app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
async def proxy(path):
    """
    این تابع برای هر درخواست یک مرورگر جدید راه‌اندازی می‌کند.
    این روش کندتر اما بسیار پایدارتر است.
    """
    
    target_url = f"{TARGET_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    if request.query_string:
        target_url += "?" + request.query_string.decode('utf-8')

    print(f"--- New Request ---")
    print(f"INFO: Launching a fresh browser instance for: {target_url}")

    try:
        async with async_playwright() as p:
            # ۱. مرورگر را راه‌اندازی کن
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu'
                ]
            )
            # ۲. یک صفحه جدید باز کن
            page = await browser.new_page()

            # ۳. به آدرس مورد نظر برو
            print("INFO: Navigating...")
            await page.goto(target_url, timeout=90000, wait_until="domcontentloaded")
            print("INFO: Page navigation complete. Getting content...")
            
            # ۴. محتوا را بگیر
            content = await page.content()
            print("SUCCESS: Content retrieved.")
            
            # ۵. مرورگر را ببند تا منابع آزاد شوند
            await browser.close()
            print("INFO: Browser instance closed.")
            
            # ۶. محتوا را برگردان
            return Response(content, status=200, mimetype="text/html")

    except PlaywrightTimeoutError:
        print(f"ERROR: Timeout (90s) occurred for {target_url}")
        return "Error: The request to the target site timed out.", 504
    except Exception as e:
        # این خطا هر مشکل دیگری را در فرآیند بالا نشان می‌دهد
        print(f"FATAL: An unexpected error occurred: {e}")
        return "Error: Failed to process the request with the proxy browser.", 500
