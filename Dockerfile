# Use official Python runtime with Alpine for smaller image
FROM python:3.11-alpine

# Set working directory
WORKDIR /app

# Install build dependencies needed for Python packages, then clean up
RUN apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev && \
    apk add --no-cache libffi

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    apk del .build-deps

# Copy application code
COPY bot.py .
COPY config/ ./config/
COPY handlers/ ./handlers/
COPY models/ ./models/
COPY utils/ ./utils/
COPY assets/ ./assets/

# Create directory for SQLite database (persistent volume will mount here)
RUN mkdir -p /data

# Run the bot
CMD ["python", "bot.py"]