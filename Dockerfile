FROM python:3.9-slim

# نصب Nginx، کروم، و ابزارهای VNC
RUN apt-get update && apt-get install -y \
    chromium \
    xvfb \
    x11vnc \
    nginx \
    git \
    net-tools \
    procps \
    && rm -rf /var/lib/apt/lists/*

# نصب NoVNC
RUN git clone https://github.com/novnc/noVNC.git /opt/novnc \
    && git clone https://github.com/novnc/websockify /opt/novnc/utils/websockify \
    && ln -s /opt/novnc/vnc.html /opt/novnc/index.html

# نصب Websockify پایتون
RUN pip install websockify

COPY app.py .

# دسترسی اجرایی به پوشه‌ها
RUN mkdir -p /var/log/nginx && \
    mkdir -p /var/lib/nginx && \
    chmod -R 777 /var/log/nginx && \
    chmod -R 777 /var/lib/nginx

EXPOSE 10000

CMD ["python", "app.py"]
