import os
import subprocess
import urllib.request
import zipfile
import stat
import gradio as gr
import threading

def run_xray(port):
    # ۱. دانلود Xray (اگر قبلاً دانلود نشده)
    if not os.path.exists("xray"):
        xray_url = "https://github.com/XTLS/Xray-core/releases/download/v1.8.24/Xray-linux-64.zip"
        urllib.request.urlretrieve(xray_url, "xray.zip")
        with zipfile.ZipFile("xray.zip", 'r') as zip_ref:
            zip_ref.extractall(".")
        st = os.stat('xray')
        os.chmod('xray', st.st_mode | stat.S_IEXEC)

    # ۲. تنظیم کانفیگ (با پورت رندر)
    config = f"""
    {{
      "log": {{ "loglevel": "none" }},
      "inbounds": [{{
        "port": {port},
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

    # ۳. اجرا
    subprocess.run(["./xray", "-c", "config.json"])

if __name__ == "__main__":
    # رندر پورت را در این متغیر می‌گذارد، اگر نبود از ۱۰۰۰۰ استفاده کن
    render_port = int(os.environ.get("PORT", 10000))
    
    # اجرای Xray در پس‌زمینه
    threading.Thread(target=run_xray, args=(render_port,), daemon=True).start()

    # ۴. اجرای یک صفحه ساده گرادیو برای راضی نگه داشتن رندر
    with gr.Blocks() as demo:
        gr.Markdown(f"# Server is Running on port {render_port}")

    demo.launch(server_name="0.0.0.0", server_port=render_port)
