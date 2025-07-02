import cloudscraper
from flask import Flask, Response, request
import random

# --- تنظیمات ---
TARGET_BASE_URL = "https://tryveo3.ai"
# -----------------

# لیست پراکسی‌های شما از webshare.io
PROXY_LIST = [
    "198.23.239.134:6540:jyzchdnp:egioy7zov8td",
    "207.244.217.165:6712:jyzchdnp:egioy7zov8td",
    "107.172.163.27:6543:jyzchdnp:egioy7zov8td",
    "23.94.138.75:6349:jyzchdnp:egioy7zov8td",
    "216.10.27.159:6837:jyzchdnp:egioy7zov8td",
    "136.0.207.84:6661:jyzchdnp:egioy7zov8td",
    "64.64.118.149:6732:jyzchdnp:egioy7zov8td",
    "142.147.128.93:6593:jyzchdnp:egioy7zov8td",
    "104.239.105.125:6655:jyzchdnp:egioy7zov8td",
    "173.0.9.70:5653:jyzchdnp:egioy7zov8td"
]

app = Flask(__name__)
scraper = cloudscraper.create_scraper()

def get_random_proxy():
    """یک پراکسی تصادفی از لیست انتخاب و فرمت می‌کند."""
    try:
        # یک پراکسی از لیست به صورت تصادفی انتخاب کن
        proxy_string = random.choice(PROXY_LIST)
        ip, port, user, password = proxy_string.split(':')
        
        # فرمت مورد نیاز برای کتابخانه requests
        proxy_url = f"http://{user}:{password}@{ip}:{port}"
        
        print(f"INFO: Using proxy: {ip}:{port}")
        
        return {
           "http": proxy_url,
           "https": proxy_url,
        }
    except Exception as e:
        print(f"ERROR: Could not parse proxy string. Error: {e}")
        return None

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    """از یک پراکسی تصادفی برای ارسال درخواست استفاده می‌کند."""
    
    target_url = f"{TARGET_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    if request.query_string:
        target_url += "?" + request.query_string.decode('utf-8')

    print(f"--- New Request ---")
    print(f"INFO: Proxying to: {target_url}")

    try:
        proxies_to_use = get_random_proxy()
        if not proxies_to_use:
            return "Error: Invalid proxy configuration in the application.", 500

        # ارسال درخواست با استفاده از پراکسی
        response = scraper.get(target_url, timeout=45, proxies=proxies_to_use)
        response.raise_for_status()
        
        print(f"SUCCESS: Got {response.status_code} from target via proxy.")
        
        content_type = response.headers.get('Content-Type', 'text/html')
        return Response(response.content, status=response.status_code, mimetype=content_type)

    except Exception as e:
        print(f"FATAL: An error occurred: {e}")
        return f"An error occurred while trying to proxy the request: {e}", 500
