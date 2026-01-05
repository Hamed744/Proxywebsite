import os
import subprocess
import time
import sys

# تنظیمات
DISPLAY = ":0"
RESOLUTION = "800x600"
PORT = os.environ.get("PORT", "10000")
TARGET_URL = "https://hadadxyz-ai.hf.space"

def log(msg):
    print(f"==> {msg}", flush=True)

def start_services():
    # 1. اجرای Xvfb (صفحه نمایش مجازی)
    log("Starting Display (Xvfb)...")
    subprocess.Popen([
        "Xvfb", DISPLAY, 
        "-screen", "0", f"{RESOLUTION}x16"
    ])
    time.sleep(3)

    # 2. اجرای x11vnc (سرور تصویر)
    log("Starting VNC Server...")
    subprocess.Popen([
        "x11vnc", 
        "-display", DISPLAY, 
        "-nopw",       # بدون پسورد
        "-forever",    # همیشه روشن بماند
        "-shared",     # اجازه چند کاربر
        "-bg"          # اجرا در پس‌زمینه
    ])
    time.sleep(2)

    # 3. اجرای فایرفاکس
    log("Starting Firefox...")
    subprocess.Popen([
        "firefox-esr",
        "--display=" + DISPLAY,
        "--width=800",
        "--height=600",
        "--kiosk",     # تمام صفحه
        TARGET_URL
    ])

    # 4. اجرای Websockify (پل ارتباطی اصلی)
    # این دستور هم فایل‌های HTML را می‌دهد و هم سوکت را برقرار می‌کند
    log(f"Starting Websockify on port {PORT}...")
    cmd = [
        "python3", "-m", "websockify",
        "--web", "/opt/novnc",  # پوشه فایل‌های HTML
        f"0.0.0.0:{PORT}",      # پورت رندر
        "localhost:5900"        # پورت داخلی VNC
    ]
    
    # این پروسه اصلی است و نباید بسته شود
    subprocess.run(cmd)

if __name__ == "__main__":
    try:
        start_services()
    except Exception as e:
        log(f"ERROR: {e}")
        sys.exit(1)
