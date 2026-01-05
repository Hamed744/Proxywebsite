# استفاده از ایمیج استاندارد و پایدار JLesage
FROM jlesage/firefox

# تنظیم پورت روی 10000 (مخصوص رندر)
ENV WEB_LISTENING_PORT=10000

# تنظیم رزولوشن (مناسب برای رم 512)
ENV DISPLAY_WIDTH=1024
ENV DISPLAY_HEIGHT=768

# تنظیم نام سرویس
ENV APP_NAME="AI-Browser"

# کپی کردن اسکریپت اجرای سایت
COPY startapp.sh /startapp.sh
RUN chmod +x /startapp.sh

# پورت رندر
EXPOSE 10000
