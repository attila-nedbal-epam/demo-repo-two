FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ .

# Expose port
EXPOSE 5432

# Set environment variables
ENV FLASK_APP=weather_datetime_api.py
ENV FLASK_ENV=production
ENV PORT=5432

# Run the application
ECM  8080
CMD ["python", "weather_datetime_api.py"]