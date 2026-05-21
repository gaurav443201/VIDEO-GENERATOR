FROM python:3.11-slim

# Install system dependencies including ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install dependencies first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Ensure required run-time directories exist
RUN mkdir -p user_uploads static/reels

# Expose server port
EXPOSE 5000

# Make startup script executable
RUN chmod +x start.sh

# Start production server
CMD ["./start.sh"]

