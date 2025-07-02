import cloudscraper
from flask import Flask, Response, request, render_template_string
import random
from urllib.parse import urlparse

# --- Settings ---
TARGET_BASE_URL = "https://tryveo3.ai"
# -----------------

PROXY_LIST = [
    "198.23.239.134:6540:jyzchdnp:egioy7zov8td", "207.244.217.165:6712:jyzchdnp:egioy7zov8td",
    "107.172.163.27:6543:jyzchdnp:egioy7zov8td", "23.94.138.75:6349:jyzchdnp:egioy7zov8td",
    "216.10.27.159:6837:jyzchdnp:egioy7zov8td", "136.0.207.84:6661:jyzchdnp:egioy7zov8td",
    "64.64.118.149:6732:jyzchdnp:egioy7zov8td", "142.147.128.93:6593:jyzchdnp:egioy7zov8td",
    "104.239.105.125:6655:jyzchdnp:egioy7zov8td", "173.0.9.70:5653:jyzchdnp:egioy7zov8td"
]

app = Flask(__name__)
scraper = cloudscraper.create_scraper()

# --- HTML Template for the main page ---
IFRAME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Proxy Viewer</title>
    <style>
        body, html { margin: 0; padding: 0; height: 100%; overflow: hidden; }
        iframe { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none; }
    </style>
</head>
<body>
    <iframe src="/proxy_content/"></iframe>
</body>
</html>
"""

def get_random_proxy():
    try:
        proxy_string = random.choice(PROXY_LIST)
        ip, port, user, password = proxy_string.split(':')
        proxy_url = f"http://{user}:{password}@{ip}:{port}"
        print(f"INFO: Using proxy: {ip}:{port}")
        return {"http": proxy_url, "https": proxy_url}
    except Exception:
        return None

@app.route('/')
def home():
    """Serves the main page with the iframe."""
    return render_template_string(IFRAME_TEMPLATE)

@app.route('/proxy_content/', defaults={'path': ''})
@app.route('/proxy_content/<path:path>')
def proxy_content(path):
    """
    This is the core proxy that fetches content for the iframe.
    It removes security headers to allow framing.
    """
    target_url = f"{TARGET_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    if request.query_string:
        target_url += "?" + request.query_string.decode('utf-8')

    print(f"--- Iframe Request ---")
    print(f"INFO: Proxying to: {target_url}")

    try:
        proxies_to_use = get_random_proxy()
        if not proxies_to_use:
            return "Error: Invalid proxy configuration.", 500

        forward_headers = {key: value for key, value in request.headers.items() if key.lower() not in ['host', 'referer']}
        forward_headers['Host'] = urlparse(TARGET_BASE_URL).netloc
        
        response = scraper.get(target_url, timeout=45, proxies=proxies_to_use, headers=forward_headers)
        response.raise_for_status()
        
        content_type = response.headers.get('Content-Type', 'text/plain')
        print(f"SUCCESS: Got {response.status_code} from target with Content-Type: {content_type}")

        # --- CRITICAL PART: Remove security headers ---
        headers_to_remove = ['content-encoding', 'transfer-encoding', 'content-security-policy', 'x-frame-options']
        final_headers = {key: value for key, value in response.headers.items() if key.lower() not in headers_to_remove}
        # ---------------------------------------------
        
        return Response(response.content, status=response.status_code, headers=final_headers)

    except Exception as e:
        print(f"FATAL: An error occurred: {e}")
        return f"An error occurred while trying to proxy the request: {e}", 500
