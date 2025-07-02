import cloudscraper
from flask import Flask, Response, request

TARGET_BASE_URL = "https://tryveo3.ai"
app = Flask(__name__)

# ترفند: یک مرورگر متفاوت را مشخص می‌کنیم
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'mobile': False
    }
)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    target_url = f"{TARGET_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    if request.query_string:
        target_url += "?" + request.query_string.decode('utf-8')

    print(f"--- New Request (Final Attempt) ---")
    print(f"INFO: Proxying with a different browser profile to: {target_url}")

    try:
        # هدرها را به صورت دستی هم تنظیم می‌کنیم تا شانس موفقیت بیشتر شود
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        response = scraper.get(target_url, timeout=30, headers=headers)
        response.raise_for_status()
        
        print(f"SUCCESS: Got {response.status_code} from target.")
        content_type = response.headers.get('Content-Type', 'text/html')
        return Response(response.text, status=response.status_code, mimetype=content_type)
    except Exception as e:
        print(f"FATAL: An error occurred: {e}")
        return f"An error occurred while trying to proxy the request: {e}", 500
