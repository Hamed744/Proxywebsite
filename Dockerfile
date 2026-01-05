FROM python:3.9-slim

# نصب ابزارهای ضروری
RUN apt-get update && apt-get install -y \
    firefox-esr \
    xvfb \
    x11vnc \
    git \
    net-tools \
    procps \
    python3-numpy \
    && rm -rf /var/lib/apt/lists/*

# نصب NoVNC (فقط فایل‌های HTML)
RUN git clone https://github.com/novnc/noVNC.git /opt/novnc \
    && git clone https://github.com/novnc/websockify /opt/novnc/utils/websockify \
    && ln -s /opt/novnc/vnc.html /opt/novnc/index.html

# نصب Websockify پایتون (برای پایداری بیشتر)
RUN pip install websockify

COPY app.py .

EXPOSE 10000

CMD ["python", "app.py"]
