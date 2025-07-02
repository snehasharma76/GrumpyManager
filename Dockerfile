# Use official Python image
FROM python:3.9-slim

# Set work directory
WORKDIR /app

# Install system dependencies (if any needed for gspread/oauth2client)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/config.py ./config/config.py
COPY get_chat_id.py ./get_chat_id.py
COPY get_updates.py ./get_updates.py
COPY direct_message_id.py ./direct_message_id.py
COPY test_setup.py ./test_setup.py

# Copy entrypoint scripts if needed (none for now)

# Expose no ports (Telegram bot is outbound only)

# Set environment variables (can be overridden at runtime)
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python", "src/main.py"] 