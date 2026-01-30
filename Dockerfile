# استفاده از نسخه پایدار Debian (Bookworm) به جای نسخه آزمایشی
FROM python:3.10-slim-bookworm

# ۱. آپدیت سیستم‌عامل برای رفع باگ‌های OpenSSL و نصب ابزارها
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y wget unzip nginx && \
    rm -rf /var/lib/apt/lists/*

# ۲. تنظیم پوشه کاری
WORKDIR /app

# ۳. دانلود نسخه جدیدتر و امن‌تر Xray (v1.8.23)
RUN wget https://github.com/XTLS/Xray-core/releases/download/v1.8.23/Xray-linux-64.zip && \
    unzip Xray-linux-64.zip && \
    chmod +x xray && \
    rm Xray-linux-64.zip

# ۴. کپی فایل پایتون
COPY app.py .

# ۵. تنظیم مجوزهای دسترسی برای کاربر ۱۰۰۱۴
RUN chown -R 10014:10014 /app /var/log/nginx /var/lib/nginx /run /tmp && \
    chmod -R 777 /tmp /var/lib/nginx /var/log/nginx

# ۶. باز کردن پورت
EXPOSE 7860

# ۷. استفاده از کاربر تایید شده Choreo
USER 10014

# ۸. اجرا
CMD ["python", "app.py"]
