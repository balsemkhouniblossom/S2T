# Use Python 3.10 slim image for compatibility
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    libcairo2-dev \
    libpango1.0-dev \
    pkg-config \
    python3-dev \
    musl-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install azure-ai-openai==1.0.0b5

# Copy application code
COPY . /app/

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install -r requirements.txt

# Collect static files (optional, for production)
# RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "training_management.wsgi:application"]
