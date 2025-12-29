FROM python:3.11-slim

# Build version: Force rebuild
ARG BUILD_VERSION=2

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy all application code first
COPY . .

# Install Python dependencies directly from pyproject.toml
RUN pip install --no-cache-dir \
    "fastapi>=0.115.0" \
    "uvicorn[standard]>=0.30.0" \
    "sqlmodel>=0.0.22" \
    "asyncpg>=0.29.0" \
    "python-jose[cryptography]>=3.3.0" \
    "passlib[bcrypt]>=1.7.4" \
    "httpx>=0.27.0" \
    "python-dotenv>=1.0.0" \
    "greenlet>=3.0.0"

# Expose Hugging Face default port
EXPOSE 7860

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
