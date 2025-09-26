# Use an official Python base image
FROM python:3.12

# Set environment variables to reduce Python buffering and prevent .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory in container
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your code
COPY . .

WORKDIR /app/src

# Expose the port (matches the one used in app.run_server)
EXPOSE 8080

# Start the Dash app
CMD ["python", "app.py"]