# Dockerfile for Verdiscan Blockchain REST API Service
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY verdiscan_api.py /app/verdiscan_api.py

# Environment variables
ENV SUBSTRATE_RPC_URL="http://127.0.0.1:9948"
ENV HOST="0.0.0.0"
ENV PORT="4400"

EXPOSE 4400

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:4400/health || exit 1

CMD ["uvicorn", "verdiscan_api:app", "--host", "0.0.0.0", "--port", "4400"]
