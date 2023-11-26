# Use a specific, slim, and secure version of the Python image for building
FROM python:3.8.14-slim-bullseye as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        default-libmysqlclient-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Install dependencies in a virtual environment
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Start of the final image
FROM python:3.8.14-slim-bullseye

# Install runtime MySQL client libraries
RUN apt-get update && \
    apt-get install -y --no-install-recommends libmariadb3 libmariadb-dev-compat && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set environment path to include the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Create a non-root user for running the application
RUN useradd --create-home appuser
USER appuser

# Set the working directory in the container
WORKDIR /app

# Copy only the necessary application files to the container
COPY --chown=appuser:appuser . .

# Expose the port the app runs on
EXPOSE 8000