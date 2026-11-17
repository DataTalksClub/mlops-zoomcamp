FROM python:3.11-slim
RUN pip install --no-cache-dir --default-timeout=120 --retries 10 mlflow==3.17.0
EXPOSE 5000
CMD ["mlflow", "server", "--host", "0.0.0.0", "--port", "5000", \
     "--backend-store-uri", "sqlite:////mlflow/mlflow.db", \
     "--serve-artifacts", "--artifacts-destination", "/mlflow/artifacts", \
     "--allowed-hosts", "*"]