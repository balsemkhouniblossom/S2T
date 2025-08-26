# Use Python 3.12
FROM python:3.12-slim

WORKDIR /app

# Copy project
COPY . /app/

# Create virtualenv (optional)
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install requirements
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Install spacy model separately
RUN python -m spacy download en_core_web_sm

# Command to run your app (update as needed)
CMD ["gunicorn", "training_management.wsgi:application", "--bind", "0.0.0.0:8000"]
