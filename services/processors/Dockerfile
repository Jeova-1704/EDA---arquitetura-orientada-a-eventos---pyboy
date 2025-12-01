FROM python:3.12-slim

LABEL maintainer="Pokemon Event System"
LABEL description="Event Processors - Microservices for event processing"

WORKDIR /app

COPY pyproject.toml ./

RUN pip install --no-cache-dir pika>=1.3.2

COPY rabbitmq_bus.py ./
COPY event_bus.py ./

COPY services/processors/ ./

ENV PYTHONUNBUFFERED=1
ENV RABBITMQ_HOST=rabbitmq
ENV RABBITMQ_PORT=5672

CMD ["python", "processor_step.py"]
