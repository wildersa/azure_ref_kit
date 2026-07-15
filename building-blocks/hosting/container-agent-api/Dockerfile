# Use a slim Python image for a smaller footprint
FROM python:3.12-slim

# Set environment variables
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files to disk
# PYTHONUNBUFFERED: Prevents Python from buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# Set work directory
WORKDIR /app

# Create a non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and change ownership
COPY --chown=appuser:appuser src/ /app/src/

# Switch to the non-root user
USER appuser

# Expose the port
EXPOSE 8080

# Run the API using the python entrypoint to respect the PORT environment variable
CMD ["python", "src/main.py"]
