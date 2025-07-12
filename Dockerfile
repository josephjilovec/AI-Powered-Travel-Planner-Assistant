# Dockerfile for AI-Powered Travel Planner Assistant

# Use an official Python runtime as a parent image.
# We choose a specific version (e.g., 3.9-slim-buster) for stability and smaller image size.
FROM python:3.9-slim-buster

# Set the working directory in the container.
# All subsequent commands will run from this directory.
WORKDIR /app

# Install system dependencies required for some Python packages.
# This step is optional and depends on your specific Python dependencies.
# For example, if any package in requirements.txt requires C headers or specific libraries,
# they would be installed here. For a basic Flask app with httpx and dotenv, this might not be strictly needed,
# but it's good practice for general Python projects.
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container at /app.
# We do this separately to leverage Docker's layer caching.
# If requirements.txt doesn't change, this layer won't be rebuilt.
COPY requirements.txt .

# Install any needed Python packages specified in requirements.txt.
# Using --no-cache-dir to save space by not storing pip's cache.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code into the container at /app.
# This includes src/, data/, public/, etc.
COPY . .

# Ensure the data directories for mock data and any potential future persistent storage exist.
# This prevents errors if the application tries to write to these paths and they don't exist.
RUN mkdir -p /app/data

# Expose the port that the Flask application will listen on.
# Flask's default development server listens on port 5000.
EXPOSE 5000

# Define environment variables for Flask.
# These are used by Flask to know where the application is and how to run it.
ENV FLASK_APP=src/app.py
# Set FLASK_RUN_HOST to 0.0.0.0 to make the Flask development server accessible
# from outside the container (i.e., from your host machine or other containers).
ENV FLASK_RUN_HOST=0.0.0.0
# Set FLASK_DEBUG to 0 for production deployments.
# DO NOT use debug mode in production as it can expose sensitive information.
ENV FLASK_DEBUG=0

# Command to run the application.
# This specifies the command that will be executed when the container starts.
# We use 'python -m flask run' for simplicity.
# For a production environment, you would typically use a more robust WSGI server
# like Gunicorn (e.g., CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "src.app:app"]).
CMD ["python", "-m", "flask", "run", "--port=5000"]

# Note on API Keys:
# It is CRITICAL to NOT hardcode your GEMINI_API_KEY or other sensitive keys directly in the Dockerfile.
# Instead, pass them at runtime as environment variables when running the Docker container,
# or use a secrets management solution.
# Example: docker run -p 5000:5000 -e GEMINI_API_KEY="your_key" ai-travel-planner-app
