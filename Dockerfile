# Use Python 3.11 slim (safer for psycopg2 & pycairo)
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies first
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    musl-dev \
    libgirepository1.0-dev \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app/

# Create virtualenv (optional)
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install azure-ai-openai==1.0.1b1

# Install spacy model
RUN python -m spacy download en_core_web_sm

# Command to run your app
CMD ["gunicorn", "training_management.wsgi:application", "--bind", "0.0.0.0:8000"]
