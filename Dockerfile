# Use official Python image
FROM python:3.9-bullseye

WORKDIR /app

ENV PYTHONPATH="/app"
COPY ./ /app

# RUN apt-get update && apt-get install -y && rm -rf /var/lib/apt/lists/*

RUN chmod +x freeze.sh && chmod +x start.sh && pip install --upgrade pip && pip install -r requirements.txt

RUN mkdir -p /app/data/faiss_index
# Expose FastAPI port
EXPOSE 8000

# Run the app

CMD ["sleep", "infinity"]
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
