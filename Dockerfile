FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies from the webapp subfolder
COPY Assignment-1-Topsis/webapp/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the webapp sources
COPY Assignment-1-Topsis/webapp/ .

# App listens on $PORT; expose common default for HF
EXPOSE 7860

CMD ["python", "app.py"]
