FROM python:3.10-slim

# ۱. نصب پیش‌نیازها
RUN apt-get update && \
    apt-get install -y wget unzip nginx && \
    rm -rf /var/lib/apt/lists/*

# ۲. ساخت پوشه کاری
WORKDIR /app

# ۳. دانلود و آماده‌سازی Xray
RUN wget https://github.com/XTLS/Xray-core/releases/download/v1.8.4/Xray-linux-64.zip && \
    unzip Xray-linux-64.zip && \
    chmod +x xray && \
    rm Xray-linux-64.zip

# ۴. کپی فایل پایتون
COPY app.py .

# ۵. دادن دسترسی کامل به همه پوشه‌های مورد نیاز برای پورت ۷۸۶۰ و اجرا
# این دستور به کاربر ۱۰۰۱۴ اجازه دسترسی به همه جا را می‌دهد
RUN chown -R 10014:10014 /app /var/log/nginx /var/lib/nginx /run /tmp && \
    chmod -R 777 /tmp /var/lib/nginx /var/log/nginx

# ۶. باز کردن پورت
EXPOSE 7860

# ۷. بخش حیاتی: فقط عدد بنویس (دقیقاً طبق خواسته Choreo)
USER 10014

# ۸. اجرای برنامه
CMD ["python", "app.py"]
