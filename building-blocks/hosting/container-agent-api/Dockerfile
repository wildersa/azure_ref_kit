# Use a slim Python image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Set work directory
WORKDIR /app

# Install dependencies
# Minimal dependencies for the reference API
RUN pip install --no-cache-dir fastapi uvicorn pydantic

# Copy source code
COPY src/ /app/src/

# Expose the port
EXPOSE 8080

# Run the API
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
