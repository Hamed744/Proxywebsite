FROM python:3.10-slim

# 1. ساخت کاربر با شناسه مجاز (اول کار انجام میدهیم)
RUN useradd -m -u 10001 appuser

# 2. نصب ابزارها
RUN apt-get update && \
    apt-get install -y wget unzip nginx && \
    rm -rf /var/lib/apt/lists/*

# 3. تنظیم پوشه کاری (خیلی مهم برای اینکه فایل‌ها جای درستی ساخته شوند)
WORKDIR /app

# 4. دانلود Xray
RUN wget https://github.com/XTLS/Xray-core/releases/download/v1.8.4/Xray-linux-64.zip && \
    unzip Xray-linux-64.zip && \
    chmod +x xray && \
    rm Xray-linux-64.zip

# 5. کپی کردن فایل پایتون
COPY app.py .

# 6. *** بخش حیاتی: دادن مجوز به کاربر 10001 ***
# ما مالکیت پوشه برنامه و پوشه‌های Nginx را به کاربر جدید می‌دهیم
RUN chown -R 10001:10001 /app && \
    chown -R 10001:10001 /var/log/nginx && \
    chown -R 10001:10001 /var/lib/nginx && \
    touch /run/nginx.pid && \
    chown 10001:10001 /run/nginx.pid

# 7. باز کردن پورت
EXPOSE 7860

# 8. تغییر به کاربر محدود شده
USER 10001

# 9. اجرا
CMD ["python", "app.py"]
