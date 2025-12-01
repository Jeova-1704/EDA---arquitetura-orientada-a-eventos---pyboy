@echo off
REM ======================================================================
REM   Pokemon Red - Microservices + Interface Grafica
REM ======================================================================
echo.
echo ======================================================================
echo   POKEMON RED - Microservicos com Interface Grafica
echo ======================================================================
echo.
echo Iniciando microservicos...
echo.

REM Subir apenas os microservicos (sem game-service)
docker compose up -d rabbitmq api-gateway report-service processor-battle processor-step processor-health processor-position

echo.
echo ======================================================================
echo   Aguardando RabbitMQ ficar pronto (10 segundos)...
echo ======================================================================
timeout /t 10 /nobreak

echo.
echo ======================================================================
echo   Microservicos rodando!
echo   - RabbitMQ: http://localhost:15672 (pokemon/pokemon123)
echo   - API: http://localhost:8000/stats
echo ======================================================================
echo.
echo Iniciando jogo com interface grafica...
echo.

REM Rodar jogo localmente com interface
python run_game_local.py

echo.
echo ======================================================================
echo   Jogo encerrado. Parando microservicos...
echo ======================================================================
docker compose down

echo.
echo Sistema encerrado!
pause
