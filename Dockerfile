# Use official Python runtime
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

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