# Use a base image that has Python and system dependencies installed
FROM python:3.9-bullseye

# Install build tools and dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    libomp-dev \
    libffi-dev \
    && apt-get clean
    
RUN apt-get update && apt-get install -y poppler-utils tesseract-ocr

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the code into the container
COPY . /app

# Set the working directory
WORKDIR /app

# Run the application
CMD ["python", "main.py"]
