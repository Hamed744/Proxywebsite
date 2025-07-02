# 1. Base Image: Use a standard Python slim image
FROM python:3.11-slim-bookworm

# 2. Set Environment Variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Set Working Directory
WORKDIR /app

# 4. Install system dependencies required by Playwright browsers
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdbus-1-3 \
    libdrm2 libgbm1 libgtk-3-0 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 \
    libxdamage1 libxext6 libxfixes3 libxrandr2 libxtst6 ca-certificates \
    fonts-liberation libappindicator3-1 lsb-release xdg-utils wget \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Install Playwright browsers
RUN playwright install --with-deps chromium

# 7. Copy the rest of the application code
COPY app.py .

# 8. Expose the port the app runs on
EXPOSE 7860

# 9. Set the command to run the application
# FINAL FIX: Use the 'gthread' worker, which is compatible with Flask's async model.
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "1", "--threads", "8", "--worker-class", "gthread", "app:app"]
