import os
import subprocess
import time

# تنظیمات نمایش
DISPLAY = ":0"
# رزولوشن را کمی کمتر کردیم تا روی رم 512 رندر روان‌تر اجرا شود
RESOLUTION = "1024x768" 
TARGET_URL = "https://hadadxyz-ai.hf.space"
RENDER_PORT = "10000"

def start_virtual_display():
    print("Initializing Graphics Core...")
    # اجرای صفحه نمایش مجازی
    subprocess.Popen(["Xvfb", DISPLAY, "-screen", "0", f"{RESOLUTION}x16"])
    time.sleep(3) # صبر برای لود شدن

def start_vnc_server():
    print("Starting VNC Protocol...")
    # اجرای سرور تصویر
    subprocess.Popen(["x11vnc", "-display", DISPLAY, "-nopw", "-forever", "-quiet", "-bg"])

def start_firefox():
    print("Launching Browser Engine...")
    # اجرای فایرفاکس در حالت کیوسک (تمام صفحه و سبک)
    subprocess.Popen([
        "firefox-esr",
        "--display=" + DISPLAY,
        "--kiosk",
        "--no-remote",
        TARGET_URL
    ])

def start_novnc_proxy():
    print(f"Starting Web Interface on port {RENDER_PORT}...")
    # تبدیل VNC به وب‌سایت قابل نمایش در مرورگر
    cmd = [
        "/opt/novnc/utils/novnc_proxy",
        "--vnc", "localhost:5900",
        "--listen", RENDER_PORT
    ]
    subprocess.Popen(cmd)

if __name__ == "__main__":
    # ترتیب اجرا بسیار مهم است
    start_virtual_display()
    start_vnc_server()
    start_firefox()
    start_novnc_proxy()
    
    print("System Online. Access via browser.")
    
    # حلقه بی‌نهایت برای باز نگه داشتن برنامه
    while True:
        time.sleep(60)
