import cloudscraper
from flask import Flask, Response, request
import random
from urllib.parse import urlparse

# --- Settings ---
TARGET_BASE_URL = "https://tryveo3.ai/features/v3"
# -----------------

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
    try:
        proxy_string = random.choice(PROXY_LIST)
        ip, port, user, password = proxy_string.split(':')
        proxy_url = f"http://{user}:{password}@{ip}:{port}"
        print(f"INFO: Using proxy: {ip}:{port}")
        return {"http": proxy_url, "https": proxy_url}
    except Exception:
        return None

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'HEAD', 'PUT', 'DELETE'])
@app.route('/<path:path>', methods=['GET', 'POST', 'HEAD', 'PUT', 'DELETE'])
def proxy(path):
    target_url = f"{TARGET_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    if request.query_string:
        target_url += "?" + request.query_string.decode('utf-8')

    print(f"--- Request for: {path} ---")

    try:
        proxies_to_use = get_random_proxy()
        if not proxies_to_use:
            return "Error: Invalid proxy configuration.", 500

        # Pass original headers from the browser (like User-Agent)
        headers = {key: value for (key, value) in request.headers if key.lower() != 'host'}
        headers['Host'] = urlparse(TARGET_BASE_URL).netloc
        
        response = scraper.request(
            method=request.method,
            url=target_url,
            proxies=proxies_to_use,
            headers=headers,
            data=request.get_data(),
            allow_redirects=False,
            timeout=45
        )

        content_type = response.headers.get('Content-Type', '')
        
        # --- CRITICAL CHANGE: SMART REWRITING ---
        if 'text/html' in content_type:
            print(f"INFO: Rewriting HTML content from {path}")
            # Replace the target domain with our proxy's domain
            content = response.text.replace(TARGET_BASE_URL, request.host_url.rstrip('/'))
            # Also replace relative paths that start with a slash
            content = content.replace('href="/', f'href="{request.host_url.rstrip("/")}/')
            content = content.replace('src="/', f'src="{request.host_url.rstrip("/")}/')
            
            # Use the rewritten content
            final_content = content.encode('utf-8')
        else:
            # For all other content types (CSS, JS, images), pass them through directly
            print(f"INFO: Passing through content type: {content_type}")
            final_content = response.content
        # ----------------------------------------
        
        # Exclude headers that can cause issues
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        final_headers = [(name, value) for (name, value) in response.raw.headers.items() if name.lower() not in excluded_headers]

        return Response(final_content, response.status_code, final_headers)

    except Exception as e:
        print(f"FATAL: An error occurred for path '{path}': {e}")
        return f"An error occurred: {e}", 500
