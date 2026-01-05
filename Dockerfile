FROM python:3.9-slim

# نصب ابزارهای ضروری و فایرفاکس
# ما git را هم اضافه کردیم برای دانلود NoVNC
RUN apt-get update && apt-get install -y \
    firefox-esr \
    xvfb \
    x11vnc \
    git \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# دانلود و نصب دستی NoVNC (چون در مخازن ساده نیست)
RUN git clone https://github.com/novnc/noVNC.git /opt/novnc \
    && git clone https://github.com/novnc/websockify /opt/novnc/utils/websockify \
    && ln -s /opt/novnc/vnc.html /opt/novnc/index.html

COPY app.py .

# پورت استاندارد رندر
ENV PORT=10000
EXPOSE 10000

CMD ["python", "app.py"]
