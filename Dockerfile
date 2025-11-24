# Dockerfile para Processadores de Eventos
FROM python:3.12-slim

# Metadata
LABEL maintainer="Pokemon Event System"
LABEL description="Event processors for Pokemon Red monitoring"

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN pip install --no-cache-dir pika

# Copy application files
COPY event_bus.py .
COPY rabbitmq_bus.py .
COPY event_processors.py .
COPY processor_*.py ./

# Default command (will be overridden by docker-compose)
CMD ["python", "processor_step.py"]
