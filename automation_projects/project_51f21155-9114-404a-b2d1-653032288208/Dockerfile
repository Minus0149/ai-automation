# Automation Project Docker Image
FROM python:3.11-slim

# Install system dependencies for browsers
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg \
    software-properties-common \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs screenshots results

# Set environment variables
ENV PYTHONPATH=/app/src
ENV DISPLAY=:99

# Run the automation
CMD ["python", "src/main_automation.py"]
