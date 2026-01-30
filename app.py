import os
import subprocess
import urllib.request
import zipfile
import stat
import gradio as gr
import threading
import time

# دریافت پورت از رندر
PORT = int(os.environ.get("PORT", 10000))

def run_xray():
    try:
        # ۱. دانلود نسخه فشرده و کوچک Xray
        if not os.path.exists("xray"):
            print("Downloading Xray...")
            xray_url = "https://github.com/XTLS/Xray-core/releases/download/v1.8.24/Xray-linux-64.zip"
            urllib.request.urlretrieve(xray_url, "xray.zip")
            with zipfile.ZipFile("xray.zip", 'r') as zip_ref:
                zip_ref.extractall(".")
            os.chmod('xray', os.stat('xray').st_mode | stat.S_IEXEC)
            print("Xray Downloaded.")

        # ۲. ساخت کانفیگ
        config = f"""
        {{
          "log": {{ "loglevel": "none" }},
          "inbounds": [{{
            "port": {PORT},
            "protocol": "vless",
            "settings": {{
              "clients": [{{ "id": "11111111-2222-3333-4444-555555555555", "level": 0 }}],
              "decryption": "none"
            }},
            "streamSettings": {{ "network": "ws", "wsSettings": {{ "path": "/vl" }} }}
          }}],
          "outbounds": [{{ "protocol": "freedom" }}]
        }}
        """
        with open("config.json", "w") as f:
            f.write(config)

        print(f"Starting Xray on port {PORT}...")
        subprocess.run(["./xray", "-c", "config.json"])
    except Exception as e:
        print(f"Error starting Xray: {e}")

# اجرای Xray در یک ترد جداگانه
threading.Thread(target=run_xray, daemon=True).start()

# ۳. اجرای بلافاصله گرادیو (بدون معطلی)
with gr.Blocks() as demo:
    gr.Markdown(f"## Server Status: Running\nChecking port {PORT}...")

if __name__ == "__main__":
    print("Launching Gradio...")
    # حتماً باید روی 0.0.0.0 باشد تا رندر پورت را ببیند
    demo.launch(server_name="0.0.0.0", server_port=PORT)
