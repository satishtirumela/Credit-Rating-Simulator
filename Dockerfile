# Production Dockerfile for Credit Rating Simulator FastAPI app on Google Cloud Run

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code, criteria PDF corpus, and JSON schemas
COPY app/ ./app/
COPY corpus/ ./corpus/
COPY schemas/ ./schemas/

# Expose container port
EXPOSE 8080

# Entrypoint command running Uvicorn on Cloud Run's dynamic PORT
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
