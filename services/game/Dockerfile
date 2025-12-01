
FROM python:3.12-slim

LABEL maintainer="Pokemon Event System"
LABEL description="Game Service - Pokemon Red Emulator with Event Publishing and SDL2 GUI"

RUN apt-get update && apt-get install -y \
    libsdl2-2.0-0 \
    libsdl2-dev \
    x11-apps \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml ./

RUN pip install --no-cache-dir pyboy>=2.6.1 pika>=1.3.2

COPY rabbitmq_bus.py ./
COPY game_monitor.py ./
COPY event_bus.py ./

COPY services/game/ ./


ENV PYTHONUNBUFFERED=1
ENV RABBITMQ_HOST=rabbitmq
ENV RABBITMQ_PORT=5672
ENV ROM_PATH="/app/rom/Pokemon - Red Version (USA, Europe) (SGB Enhanced).gb"
ENV HEADLESS=false
ENV DISPLAY=:0

CMD ["python", "game_service.py"]
