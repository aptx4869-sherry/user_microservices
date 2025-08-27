# Use Python 3.8 slim as base
FROM python:3.8-slim

# Set working directory in container
WORKDIR /app

# Install required system packages
RUN apt-get update && \
    apt-get install -y curl gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything into /app
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Run FastAPI app
CMD ["uvicorn", "espresso_engine.main_cafe_server:app", "--host", "0.0.0.0", "--port", "8000"]
