FROM python:3.11-slim
WORKDIR /app
COPY requirements-docker.txt .
RUN pip install --no-cache-dir --default-timeout=120 --retries 10 -r requirements-docker.txt
COPY common ./common
COPY pipeline ./pipeline
COPY agents ./agents
COPY rules ./rules
ENV PYTHONPATH=/app
