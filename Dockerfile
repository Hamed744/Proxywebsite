# 1. Base Image: A simple and standard Python image
FROM python:3.11-slim-bookworm

# 2. Set Working Directory
WORKDIR /app

# 3. Copy requirements.txt and install the lightweight dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the application code
COPY app.py .

# 5. Expose the port
EXPOSE 7860

# 6. Set the command to run the application
# We can use more workers now because the app is very lightweight.
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "4", "app:app"]
