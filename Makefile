# Makefile para Pokemon Event-Driven Microservices
# Comandos simplificados para gerenciar a arquitetura

.PHONY: help build up down logs clean restart status scale-step health api

# Cores para output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Mostra esta ajuda
	@echo "$(BLUE)Pokemon Event-Driven Microservices - Comandos Disponíveis:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

build: ## Build de todas as imagens Docker
	@echo "$(BLUE)🔨 Building Docker images...$(NC)"
	docker-compose build

up: ## Inicia todos os serviços
	@echo "$(BLUE)🚀 Iniciando serviços...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✅ Serviços iniciados!$(NC)"
	@echo ""
	@echo "$(YELLOW)📊 Acesse:$(NC)"
	@echo "  RabbitMQ Management: http://localhost:15672 (pokemon/pokemon123)"
	@echo "  API Gateway:         http://localhost:8000"
	@echo ""

down: ## Para todos os serviços
	@echo "$(BLUE)🛑 Parando serviços...$(NC)"
	docker-compose down
	@echo "$(GREEN)✅ Serviços parados!$(NC)"

logs: ## Mostra logs de todos os serviços
	docker-compose logs -f

logs-game: ## Mostra logs do Game Service
	docker-compose logs -f game-service

logs-api: ## Mostra logs do API Gateway
	docker-compose logs -f api-gateway

logs-report: ## Mostra logs do Report Service
	docker-compose logs -f report-service

logs-battle: ## Mostra logs do Battle Processor
	docker-compose logs -f processor-battle

logs-step: ## Mostra logs do Step Processor
	docker-compose logs -f processor-step

logs-health: ## Mostra logs do Health Processor
	docker-compose logs -f processor-health

logs-position: ## Mostra logs do Position Processor
	docker-compose logs -f processor-position

logs-rabbitmq: ## Mostra logs do RabbitMQ
	docker-compose logs -f rabbitmq

clean: ## Remove todos os containers, volumes e networks
	@echo "$(RED)⚠️  Removendo TUDO (containers, volumes, networks)...$(NC)"
	docker-compose down -v --remove-orphans
	@echo "$(GREEN)✅ Limpeza completa!$(NC)"

restart: down up ## Reinicia todos os serviços

restart-game: ## Reinicia apenas o Game Service
	docker-compose restart game-service

restart-api: ## Reinicia apenas o API Gateway
	docker-compose restart api-gateway

restart-report: ## Reinicia apenas o Report Service
	docker-compose restart report-service

status: ## Mostra status de todos os serviços
	@echo "$(BLUE)📊 Status dos Serviços:$(NC)"
	@docker-compose ps

ps: status ## Alias para status

scale-step: ## Escala Step Processor (ex: make scale-step N=3)
	@echo "$(BLUE)📈 Escalando Step Processor para $(N) instâncias...$(NC)"
	docker-compose up -d --scale processor-step=$(N)
	@echo "$(GREEN)✅ Escalado!$(NC)"

health: ## Verifica saúde dos serviços
	@echo "$(BLUE)🏥 Verificando saúde dos serviços...$(NC)"
	@echo ""
	@echo "$(YELLOW)RabbitMQ:$(NC)"
	@curl -s -u pokemon:pokemon123 http://localhost:15672/api/overview | grep -o '"rabbitmq_version":"[^"]*"' || echo "❌ RabbitMQ não acessível"
	@echo ""
	@echo "$(YELLOW)API Gateway:$(NC)"
	@curl -s http://localhost:8000/health | grep -o '"status":"[^"]*"' || echo "❌ API Gateway não acessível"
	@echo ""

api: ## Abre documentação da API no navegador
	@echo "$(BLUE)📖 Abrindo API documentation...$(NC)"
	@powershell.exe -Command "Start-Process 'http://localhost:8000'"

rabbitmq-ui: ## Abre RabbitMQ Management UI no navegador
	@echo "$(BLUE)🐰 Abrindo RabbitMQ Management...$(NC)"
	@powershell.exe -Command "Start-Process 'http://localhost:15672'"

stats: ## Mostra estatísticas via API
	@echo "$(BLUE)📊 Estatísticas do Jogo:$(NC)"
	@curl -s http://localhost:8000/stats | python -m json.tool

rebuild: down build up ## Rebuild completo (down, build, up)

install: ## Instala dependências Python localmente
	@echo "$(BLUE)📦 Instalando dependências...$(NC)"
	pip install pyboy pika flask flask-cors
	@echo "$(GREEN)✅ Dependências instaladas!$(NC)"

test-connection: ## Testa conexão com RabbitMQ
	@echo "$(BLUE)🔌 Testando conexão com RabbitMQ...$(NC)"
	@python -c "import pika; conn = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672, credentials=pika.PlainCredentials('pokemon', 'pokemon123'))); print('✅ Conexão OK!'); conn.close()" || echo "❌ Falha na conexão"

# Comandos de desenvolvimento
dev-up: ## Inicia apenas RabbitMQ (para desenvolvimento local)
	docker-compose up -d rabbitmq
	@echo "$(GREEN)✅ RabbitMQ iniciado para desenvolvimento!$(NC)"

dev-down: ## Para apenas RabbitMQ
	docker-compose stop rabbitmq

# Informações
info: ## Mostra informações do sistema
	@echo "$(BLUE)ℹ️  Informações do Sistema:$(NC)"
	@echo ""
	@echo "$(YELLOW)Serviços:$(NC)"
	@docker-compose ps --format json | python -m json.tool 2>/dev/null || docker-compose ps
	@echo ""
	@echo "$(YELLOW)Networks:$(NC)"
	@docker network ls | grep pokemon
	@echo ""
	@echo "$(YELLOW)Volumes:$(NC)"
	@docker volume ls | grep pokemon
	@echo ""
