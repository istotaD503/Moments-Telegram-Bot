# Use ultra-minimal Python Alpine image
FROM python:3.11-alpine3.19

# Set working directory
WORKDIR /app

# Install dependencies in single layer to minimize image size
COPY requirements.txt .
RUN apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del .build-deps && \
    rm -rf /root/.cache /tmp/*

# Copy application code
COPY bot.py .
COPY config/ ./config/
COPY handlers/ ./handlers/
COPY models/ ./models/
COPY utils/ ./utils/
COPY assets/ ./assets/

# Create directory for SQLite database (persistent volume will mount here)
RUN mkdir -p /data

# Set Python environment variables for memory optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONOPTIMIZE=1

# Run the bot with optimizations
CMD ["python", "-OO", "bot.py"]