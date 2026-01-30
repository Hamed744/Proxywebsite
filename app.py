import os
import subprocess
import urllib.request
import zipfile
import stat
import gradio as gr
import threading

def run_xray():
    # ۱. دانلود Xray
    if not os.path.exists("xray"):
        xray_url = "https://github.com/XTLS/Xray-core/releases/download/v1.8.24/Xray-linux-64.zip"
        urllib.request.urlretrieve(xray_url, "xray.zip")
        with zipfile.ZipFile("xray.zip", 'r') as zip_ref:
            zip_ref.extractall(".")
        st = os.stat('xray')
        os.chmod('xray', st.st_mode | stat.S_IEXEC)

    # ۲. تنظیم کانفیگ
    config = """
    {
      "log": { "loglevel": "none" },
      "inbounds": [{
        "port": 7860,
        "protocol": "vless",
        "settings": {
          "clients": [{"id": "11111111-2222-3333-4444-555555555555", "level": 0}],
          "decryption": "none"
        },
        "streamSettings": { "network": "ws", "wsSettings": { "path": "/vl" } }
      }],
      "outbounds": [{"protocol": "freedom"}]
    }
    """
    with open("config.json", "w") as f:
        f.write(config)

    # ۳. اجرا
    subprocess.run(["./xray", "-c", "config.json"])

# اجرای Xray در یک ترد جداگانه که برنامه پایتون متوقف نشود
threading.Thread(target=run_xray, daemon=True).start()

# ۴. ساخت یک رابط کاربری ساده گرادیو (برای اینکه سایت راضی بماند)
with gr.Blocks() as demo:
    gr.Markdown("# Server is Running")
    gr.Markdown("The inference node is operational.")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
