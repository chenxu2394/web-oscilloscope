# Use an official Python 3.7 slim image
FROM python:3.7.13-slim

# Install system dependencies including Nginx
RUN apt-get update && \
    apt-get install -y nginx && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install required Python packages from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the oscilloscope script into the container
COPY oscilloscope.py .

# Copy the Nginx configuration file to override the default site configuration
COPY nginx.conf /etc/nginx/sites-available/default

# Copy the startup script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Set Bokeh allowed websocket origin to localhost:8080
ENV BOKEH_ALLOW_WS_ORIGIN=localhost:8080

# Expose port 80 (the port Nginx listens on)
EXPOSE 80

# Use the startup script as the container entrypoint
CMD ["/app/start.sh"]
