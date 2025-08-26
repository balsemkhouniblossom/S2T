FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed for psycopg2, pycairo, manimpango
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    libcairo2-dev \
    libpango1.0-dev \
    pkg-config \
    python3-dev \
    musl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app/

# Create virtualenv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install azure-ai-openai==1.0.1b1

# Install spacy model
RUN python -m spacy download en_core_web_sm

# Command to run the app
CMD ["gunicorn", "training_management.wsgi:application", "--bind", "0.0.0.0:8000"]
