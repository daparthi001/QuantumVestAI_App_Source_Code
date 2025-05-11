# Use official Python image as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy current directory contents into the container
COPY . /app/

# Install dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Expose port
EXPOSE 8000

# Run the app
CMD ["python", "main.py"]