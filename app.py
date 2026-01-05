import os
import subprocess
import time
import sys

# تنظیمات
DISPLAY = ":0"
RESOLUTION = "1024x768" # رزولوشن مناسب
PORT = os.environ.get("PORT", "10000")
TARGET_URL = "https://hadadxyz-ai.hf.space"

def log(msg):
    print(f"==> {msg}", flush=True)

def setup_nginx():
    log("Configuring Nginx...")
    conf = f"""
worker_processes 1;
daemon off;
pid /tmp/nginx.pid;
events {{ worker_connections 1024; }}

http {{
    include /etc/nginx/mime.types;
    access_log off;
    error_log /dev/stderr;

    server {{
        listen {PORT};
        server_name _;

        # 1. نمایش فایل‌های NoVNC
        location / {{
            root /opt/novnc;
            index vnc.html;
            try_files $uri $uri/ /vnc.html;
        }}

        # 2. تنظیمات حیاتی برای اتصال WebSocket (حل مشکل چرخیدن)
        location /websockify {{
            proxy_pass http://127.0.0.1:6080;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "Upgrade";
            proxy_read_timeout 86400;
        }}
    }}
}}
"""
    with open("nginx.conf", "w") as f:
        f.write(conf)

def start_services():
    # 1. ساخت کانفیگ Nginx
    setup_nginx()

    # 2. اجرای صفحه مجازی
    log("Starting Xvfb...")
    subprocess.Popen(["Xvfb", DISPLAY, "-screen", "0", f"{RESOLUTION}x16"])
    time.sleep(2)

    # 3. اجرای سرور تصویر
    log("Starting x11vnc...")
    subprocess.Popen(["x11vnc", "-display", DISPLAY, "-nopw", "-forever", "-quiet", "-bg"])

    # 4. اجرای کروم (Chromium) با تنظیمات ضد کرش
    log("Starting Chromium...")
    subprocess.Popen([
        "chromium",
        "--display=" + DISPLAY,
        "--no-sandbox",              # حیاتی برای داکر
        "--disable-dev-shm-usage",   # حیاتی برای رم کم
        "--kiosk",                   # تمام صفحه
        "--start-maximized",
        TARGET_URL
    ])

    # 5. اجرای Websockify روی پورت داخلی 6080
    log("Starting Websockify Internal...")
    subprocess.Popen([
        "python3", "-m", "websockify",
        "6080",              # پورت داخلی
        "localhost:5900"     # پورت VNC
    ])

    # 6. اجرای Nginx (مدیر اصلی)
    log(f"Starting Nginx on port {PORT}...")
    subprocess.run(["nginx", "-c", os.path.abspath("nginx.conf")])

if __name__ == "__main__":
    try:
        start_services()
    except Exception as e:
        log(f"ERROR: {e}")
        sys.exit(1)
