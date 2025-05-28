# Use official Python image
FROM python:3.9-bullseye

# Set work directory
WORKDIR /app

# Install OS dependencies
# RUN apt-get update && apt-get install -y \
#     git \
#     && rm -rf /var/lib/apt/lists/*

# Install Python packages
# RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy app files
COPY ./src /src

RUN mkdir -p /app/data/faiss_index
# Expose FastAPI port
EXPOSE 8000

# Run the app

CMD ["sleep", "infinity"]
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
