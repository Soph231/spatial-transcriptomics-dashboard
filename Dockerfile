FROM python:3.11-slim

WORKDIR /app
COPY requirements-gcs.txt .
RUN pip install --no-cache-dir -r requirements-gcs.txt
COPY . .

ENV DATA_SOURCE=gcs
ENV HOST=0.0.0.0
CMD exec gunicorn --bind :${PORT:-8080} app:server
