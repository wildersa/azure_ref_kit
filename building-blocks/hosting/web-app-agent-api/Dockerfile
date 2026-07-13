# Use a slim Python image for a smaller footprint
FROM python:3.12-slim

# Set environment variables
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

# Expose the default port (documentation only)
EXPOSE 8080

# Run the API using the Python entrypoint to ensure port-selection logic in main.py is honored.
# This ensures consistency between local runs, Docker, and Azure App Service (honoring WEBSITES_PORT).
CMD ["python", "src/main.py"]
