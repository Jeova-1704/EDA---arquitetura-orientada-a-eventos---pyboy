FROM python:3.12-slim

LABEL maintainer="Pokemon Event System"
LABEL description="API Gateway - REST API for monitoring and control"
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir pika>=1.3.2 flask>=3.0.0 flask-cors>=4.0.0
COPY rabbitmq_bus.py ./
COPY event_bus.py ./
COPY services/api/ ./
ENV PYTHONUNBUFFERED=1
ENV RABBITMQ_HOST=rabbitmq
ENV RABBITMQ_PORT=5672
ENV API_HOST=0.0.0.0
ENV API_PORT=8000
EXPOSE 8000
CMD ["python", "api_gateway.py"]
