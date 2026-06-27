# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \ 
    libfreetype6-dev \
    libjpeg-dev \
    zlib1g-dev \
    libraqm-dev \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

# Copy the pyproject.toml and poetry.lock files to the container
COPY pyproject.toml poetry.lock /app/

# Install Poetry and Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root

# Copy the rest of the application code to the container
COPY . /app

# Expose the port that the app runs on
EXPOSE 8001

# Command to run the application (skip alembic since migrations are managed by app-pecha-backend)
CMD ["uvicorn", "worker_api.app:api", "--host", "0.0.0.0", "--port", "8001"]
