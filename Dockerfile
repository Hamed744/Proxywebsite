# 1. Base Image: A simple and standard Python image
FROM python:3.11-slim-bookworm

# 2. Set Working Directory
WORKDIR /app

# 3. Copy requirements.txt and install the lightweight dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the application code
COPY app.py .

# 5. Expose the port (Render uses this)
# Gunicorn will bind to this port
EXPOSE 10000

# 6. Set the command to run the application
# Standard Gunicorn command for a Flask app
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--workers", "4", "app:app"]
