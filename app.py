import cloudscraper
from flask import Flask, Response, request
import random
import re
from urllib.parse import urlparse, urljoin

# --- Settings ---
TARGET_BASE_URL = "https://tryveo3.ai"
# -----------------

# ! IMPORTANT: Replace 'proxywebsite.onrender.com' with your actual Render URL !
# You MUST replace this value with the URL that Render assigned to your service.
# Example: MY_RENDER_URL = "https://my-awesome-proxy.onrender.com"
MY_RENDER_URL = "https://proxywebsite.onrender.com" 
# -----------------------------------------------------------------------------

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
    except Exception as e:
        print(f"ERROR: Could not parse proxy string. Error: {e}")
        return None

def rewrite_content(content, original_base_url, proxy_base_url):
    """
    Rewrites URLs in HTML content to point back to the proxy.
    Also injects a <base> tag for proper relative URL resolution.
    """
    if not isinstance(content, str): # Ensure content is string for regex operations
        try:
            content = content.decode('utf-8')
        except UnicodeDecodeError:
            content = content.decode('latin-1') # Fallback for non-UTF8 content

    # 1. Inject <base> tag: Tells the browser how to resolve relative URLs
    base_tag = f'<base href="{original_base_url.rstrip("/")}/">'
    # Try to insert after <head>, otherwise at the beginning of html
    content = re.sub(r'(<head[^>]*>)', r'\1' + base_tag, content, flags=re.IGNORECASE, count=1)
    if base_tag not in content and '<html' in content.lower(): # If no head, try after html tag
        content = re.sub(r'(<html[^>]*>)', r'\1' + base_tag, content, flags=re.IGNORECASE, count=1)
    elif base_tag not in content: # As a last resort, just prepend if it's not detected
        content = base_tag + content


    # 2. Rewrite absolute URLs pointing to the original domain
    # Example: https://tryveo3.ai/path becomes https://proxywebsite.onrender.com/path
    # This is a basic regex and might not catch all cases, but covers many common ones.
    # We escape the original_base_url to handle dots etc.
    escaped_original_url = re.escape(original_base_url)
    content = re.sub(escaped_original_url, proxy_base_url, content, flags=re.IGNORECASE)

    return content.encode('utf-8') # Return as bytes

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    target_url = f"{TARGET_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    if request.query_string:
        target_url += "?" + request.query_string.decode('utf-8')

    print(f"--- New Request ---")
    print(f"INFO: Proxying to: {target_url}")

    try:
        proxies_to_use = get_random_proxy()
        if not proxies_to_use:
            return "Error: Invalid proxy configuration.", 500

        # Pass along all headers from the client, except for a few
        excluded_headers = ['host', 'connection', 'accept-encoding', 'referer']
        forward_headers = {key: value for key, value in request.headers.items() if key.lower() not in excluded_headers}
        # Set the Host header to the target's actual host for Cloudflare
        forward_headers['Host'] = urlparse(TARGET_BASE_URL).netloc
        
        response = scraper.get(target_url, timeout=60, proxies=proxies_to_use, headers=forward_headers)
        response.raise_for_status()
        
        content_type = response.headers.get('Content-Type', 'text/plain')
        print(f"SUCCESS: Got {response.status_code} from target with Content-Type: {content_type}")

        final_content = response.content
        if 'text/html' in content_type:
            # Only rewrite HTML content
            print("INFO: Rewriting HTML content...")
            final_content = rewrite_content(response.content, TARGET_BASE_URL, MY_RENDER_URL)
            print("SUCCESS: HTML content rewritten.")
        
        # Remove potentially problematic headers
        headers_to_remove = ['content-encoding', 'transfer-encoding', 'x-frame-options', 'content-security-policy']
        for header in headers_to_remove:
            if header in response.headers:
                del response.headers[header]

        # Return the response with proper content type and potentially rewritten content
        return Response(final_content, status=response.status_code, mimetype=content_type, headers=response.headers)

    except Exception as e:
        print(f"FATAL: An error occurred: {e}")
        return f"An error occurred while trying to proxy the request: {e}", 500
