# Dockerfile para Report Service
FROM python:3.12-slim

LABEL maintainer="Pokemon Event System"
LABEL description="Report Service - Consolidated Reports Generator"

WORKDIR /app

COPY pyproject.toml ./

RUN pip install --no-cache-dir pika>=1.3.2

COPY rabbitmq_bus.py ./
COPY event_bus.py ./

COPY services/reports/ ./

ENV PYTHONUNBUFFERED=1
ENV RABBITMQ_HOST=rabbitmq
ENV RABBITMQ_PORT=5672
ENV REPORT_INTERVAL=300

CMD ["python", "report_service.py"]
