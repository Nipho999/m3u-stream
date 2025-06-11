# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /m3u-stream

# Copy files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Flask will run on
EXPOSE 5000

# Run the Flask app
CMD ["python", "app-4.py"]
