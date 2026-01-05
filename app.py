import os
import subprocess
import time
import sys

# تنظیمات بهینه شده برای رندر
DISPLAY = ":0"
# رزولوشن کمتر برای مصرف رم کمتر
RESOLUTION = "800x600" 
TARGET_URL = "https://hadadxyz-ai.hf.space"
# دریافت پورت از رندر (یا پیش‌فرض 10000)
PORT = os.environ.get("PORT", "10000")

def log(msg):
    print(f"[SYSTEM] {msg}", flush=True)

def start_virtual_display():
    log("Starting Xvfb (Display)...")
    subprocess.Popen(["Xvfb", DISPLAY, "-screen", "0", f"{RESOLUTION}x16"])
    time.sleep(3)

def start_vnc_server():
    log("Starting x11vnc...")
    # اجرای VNC
    subprocess.Popen(["x11vnc", "-display", DISPLAY, "-nopw", "-forever", "-quiet", "-bg"])

def start_firefox():
    log("Starting Firefox Kiosk...")
    # اجرای فایرفاکس
    subprocess.Popen([
        "firefox-esr",
        "--display=" + DISPLAY,
        "--width=800",
        "--height=600",
        "--kiosk",
        TARGET_URL
    ])

def start_novnc_proxy():
    log(f"Starting NoVNC Proxy on port {PORT}...")
    
    # دستور حیاتی: listen روی 0.0.0.0
    cmd = [
        "/opt/novnc/utils/novnc_proxy",
        "--vnc", "localhost:5900",
        "--listen", f"0.0.0.0:{PORT}"
    ]
    
    process = subprocess.Popen(cmd)
    return process

if __name__ == "__main__":
    try:
        start_virtual_display()
        start_vnc_server()
        start_firefox()
        
        # اجرای پروکسی و ذخیره پروسه
        proxy_process = start_novnc_proxy()
        
        log(f"Service works! Open: https://YOUR-APP.onrender.com/vnc.html?autoconnect=true")
        
        # نگه داشتن برنامه و چک کردن خطا
        while True:
            if proxy_process.poll() is not None:
                log("FATAL: NoVNC Proxy crashed!")
                sys.exit(1)
            time.sleep(10)
            
    except Exception as e:
        log(f"Error: {e}")
