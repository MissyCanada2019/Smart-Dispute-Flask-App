FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV FLASK_APP=main.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Create directories
RUN mkdir -p /app/uploads
RUN mkdir -p /app/logs

# Expose port
EXPOSE 8080

# Health check configuration
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8080/health || exit 1

# Run the application with SSL support
CMD ["sh", "-c", "python manage.py init-db --env=production && gunicorn --bind 0.0.0.0:8080 --workers 4 --threads 2 --timeout 120 --certfile $SSL_CERT_PATH --keyfile $SSL_KEY_PATH --ca-certs $SSL_CERT_PATH wsgi:app"]