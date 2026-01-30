FROM python:3.10-slim-bookworm

# ۱. آپدیت کامل سیستم‌عامل
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y wget unzip nginx && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ۲. دانلود آخرین نسخه فوق امن Xray (v1.8.24)
# این نسخه با آخرین استانداردهای امنیتی ۲۰۲۵ ساخته شده
RUN wget https://github.com/XTLS/Xray-core/releases/download/v1.8.24/Xray-linux-64.zip && \
    unzip Xray-linux-64.zip && \
    chmod +x xray && \
    rm Xray-linux-64.zip

COPY app.py .

# ۳. تنظیم دسترسی‌ها برای Choreo
RUN chown -R 10014:10014 /app /var/log/nginx /var/lib/nginx /run /tmp && \
    chmod -R 777 /tmp /var/lib/nginx /var/log/nginx

EXPOSE 7860

USER 10014

CMD ["python", "app.py"]
