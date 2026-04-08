# Dockerfile for Email Triage OpenEnv
# Builds a container that runs the FastAPI environment server

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for faster rebuilds)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the server code
COPY server/ ./server/

# Copy the openenv yaml
COPY openenv.yaml .

# Copy inference script
COPY inference.py .

# Set the working directory to server for running the app
WORKDIR /app/server

# Expose port 7860 (required for Hugging Face Spaces)
EXPOSE 7860

# Start the FastAPI server
CMD ["python", "app.py"]
