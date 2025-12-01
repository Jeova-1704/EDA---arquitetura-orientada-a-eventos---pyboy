# Pokemon Red - Event-Driven Microservices Architecture

Sistema de monitoramento e controle para Pokemon Red implementando **arquitetura de microserviços orientada a eventos** com RabbitMQ como message broker.

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Arquitetura](#arquitetura)
- [Microserviços](#microserviços)
- [Quick Start](#quick-start)
- [Como Usar](#como-usar)
- [API REST](#api-rest)
- [Escalabilidade](#escalabilidade)
- [Monitoramento](#monitoramento)

---

## Sobre o Projeto

Este projeto demonstra uma **arquitetura de microserviços completa** utilizando:

- ✅ **Event-Driven Architecture** (EDA)
- ✅ **Publish/Subscribe Pattern**
- ✅ **Microservices Architecture**
- ✅ **Message Broker** (RabbitMQ)
- ✅ **REST API** (API Gateway)
- ✅ **Containerização** (Docker)
- ✅ **Escalabilidade Horizontal**
- ✅ **Resiliência** - serviços independentes

### Tecnologias

- **Python 3.12+**
- **PyBoy 2.6.1+** - Emulador Game Boy
- **RabbitMQ 3.12** - Message broker AMQP
- **Flask 3.0+** - REST API
- **Docker & Docker Compose** - Containerização

---

## Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                    VOCÊ JOGANDO (Local)                         │
│                 PyBoy com Interface SDL2                        │
└────────────────────────┬────────────────────────────────────────┘
                         │ Publica eventos
                         ▼
┌────────────────────────────────────────────────────────────────┐
│                    RABBITMQ MESSAGE BROKER                     │
│                   (Docker Container)                           │
│   - Exchange: pokemon_events (topic)                           │
│   - Queues: Exclusive temporary queues per consumer            │
│   - Ports: 5672 (AMQP), 15672 (Management UI)                 │
└──┬─────────┬──────────┬──────────┬──────────┬─────────────────┘
   │         │          │          │          │
   ▼         ▼          ▼          ▼          ▼
┌─────┐  ┌─────┐  ┌─────────┐ ┌────────┐ ┌────────────┐
│API  │  │REPORT│  │PROCESSOR│ │PROCESS.│ │PROCESSOR   │
│GTW  │  │SERV. │  │BATTLE   │ │STEP    │ │HEALTH/POS. │
└─────┘  └─────┘  └─────────┘ └────────┘ └────────────┘
(Docker) (Docker)   (Docker)    (Docker)    (Docker)
```

### Fluxo de Eventos

1. **Você joga** Pokemon Red localmente (interface SDL2)
2. **Game monitor** detecta mudanças → Publica eventos no **RabbitMQ**
3. **RabbitMQ** roteia eventos para filas específicas
4. **Processadores** (Docker) consomem eventos de forma independente
5. **Report Service** (Docker) consolida estatísticas
6. **API Gateway** (Docker) expõe dados via REST API

### Resiliência

- ✅ Se um processador cair, outros continuam funcionando
- ✅ RabbitMQ armazena mensagens persistentemente
- ✅ Containers reiniciam automaticamente (`restart: unless-stopped`)
- ✅ Filas temporárias exclusivas previnem conflitos
- ✅ Jogo roda localmente (não depende de containers)

---

## Microserviços

### 1. RabbitMQ (Docker)
**Responsabilidade:** Message broker AMQP

- Recebe eventos do jogo
- Roteia para processadores
- Persiste mensagens
- Interface web de gerenciamento

### 2. API Gateway (Docker)
**Responsabilidade:** Interface REST para o sistema

- Expõe endpoints HTTP
- Consolida estatísticas em tempo real
- Healthcheck dos serviços

**Endpoints:**
- `GET /` - Documentação
- `GET /health` - Status da API
- `GET /stats` - Todas estatísticas
- `GET /stats/battles` - Batalhas
- `GET /stats/steps` - Passos
- `GET /stats/health` - HP atual
- `GET /stats/position` - Posição
- `GET /reports` - Relatórios gerados

**Porta:** 8000

### 3. Report Service (Docker)
**Responsabilidade:** Gerar relatórios consolidados

- Coleta estatísticas de todos processadores
- Gera relatórios periódicos (5 min)
- Gera relatório final ao encerrar

### 4. Processor Services (4 microserviços no Docker)

**Battle Processor:**
- Conta batalhas
- Registra histórico

**Step Processor:**
- Conta passos
- Log a cada 10 passos
- *Escalável horizontalmente*

**Health Processor:**
- Monitora HP
- Alerta quando crítico (< 20%)

**Position Processor:**
- Rastreia posição
- Detecta mudanças de mapa

---

## Quick Start

### Pré-requisitos

- **Docker Desktop** instalado e rodando
- **Python 3.12+** instalado
- **ROM** do Pokemon Red em `rom/Pokemon - Red Version (USA, Europe) (SGB Enhanced).gb`

### Dependências Python

```bash
# Instalar dependências
pip install pyboy pika
```

---

## Como Usar

### **Opção 1: Script Automático (Recomendado)**

```bash
start.bat
```

Isso vai:
1. ✅ Subir todos os microserviços no Docker
2. ✅ Aguardar RabbitMQ ficar pronto
3. ✅ Abrir o jogo com interface gráfica
4. ✅ Você joga enquanto microserviços processam eventos!

### **Opção 2: Manual (Passo a Passo)**

```bash
# 1. Subir microserviços
docker compose up -d rabbitmq api-gateway report-service processor-battle processor-step processor-health processor-position

# 2. Aguardar RabbitMQ (10 segundos)
timeout /t 10

# 3. Rodar jogo localmente
python run_game_local.py
```

### **Opção 3: Desenvolvimento (Com Logs)**

```bash
# 1. Subir microserviços COM logs
docker compose up rabbitmq api-gateway report-service processor-battle processor-step processor-health processor-position

# 2. Em outro terminal, rodar jogo
python run_game_local.py
```

---

## 🎮 Controles do Jogo

| Tecla | Botão | Função |
|-------|-------|--------|
| **↑↓←→** | D-Pad | Movimento |
| **Z** | A | Confirmar/Interagir |
| **X** | B | Cancelar/Correr |
| **Enter** | START | Menu |
| **Backspace** | SELECT | Trocar Pokemon |
| **ESC** | - | Fechar jogo |

---

## API REST

### Acessar Interfaces

- **API Gateway:** http://localhost:8000
- **RabbitMQ Management:** http://localhost:15672
  - Usuário: `pokemon`
  - Senha: `pokemon123`

### Exemplos de Uso

```bash
# Obter todas estatísticas
curl http://localhost:8000/stats

# Apenas batalhas
curl http://localhost:8000/stats/battles

# Healthcheck
curl http://localhost:8000/health

# Relatórios gerados
curl http://localhost:8000/reports
```

### Resposta Exemplo

```json
{
  "battles": 5,
  "steps": 247,
  "health": {
    "current_hp": 18,
    "max_hp": 22,
    "percentage": 81.8
  },
  "position": {
    "current": [10, 15],
    "map_id": 1
  },
  "game": {
    "is_running": true,
    "start_time": "2024-12-01T14:30:00"
  }
}
```

---

## Escalabilidade

### Escalar Processadores Horizontalmente

```bash
# Escalar Step Processor para 3 instâncias
docker compose up -d --scale processor-step=3

# Verificar
docker compose ps processor-step
```

**Como funciona:**
- RabbitMQ faz **load balancing** automático
- Cada instância processa mensagens em paralelo
- Aumenta throughput sem modificar código

---

## Monitoramento

### Ver Logs dos Microserviços

```bash
# Todos os serviços
docker compose logs -f

# Serviço específico
docker compose logs -f processor-battle
docker compose logs -f api-gateway
```

### RabbitMQ Management UI

Acesse: http://localhost:15672

**O que monitorar:**
- **Overview:** Taxa de mensagens, conexões
- **Queues:** Mensagens prontas, não confirmadas
- **Exchanges:** Bindings ativos
- **Connections:** Consumers conectados

---

## Resiliência do Sistema

### Testar Resiliência

```bash
# Derrubar um processador
docker compose stop processor-step

# Sistema continua funcionando!
# - Jogo roda normalmente
# - Eventos são publicados
# - Outros processadores funcionam
# - Mensagens ficam na fila do RabbitMQ

# Reativar processador
docker compose start processor-step
# Processador consome mensagens acumuladas!
```

### Benefícios

- ✅ **Tolerância a falhas** - Um serviço caído não afeta outros
- ✅ **Persistência** - Mensagens não se perdem
- ✅ **Auto-recovery** - Containers reiniciam automaticamente
- ✅ **Escalabilidade** - Adicione mais processadores conforme necessário

---

## Comandos Úteis

```bash
# Iniciar tudo
start.bat

# Parar microserviços
docker compose down

# Reiniciar um serviço
docker compose restart processor-battle

# Ver status
docker compose ps

# Ver logs
docker compose logs -f

# Escalar processador
docker compose up -d --scale processor-step=3
```

---

## Estrutura de Arquivos

```
pokemon/
├── docker-compose.yml          # Orquestração dos microserviços
├── start.bat                   # Script para iniciar tudo
├── run_game_local.py           # Roda jogo localmente com interface
├── README.md                   # Esta documentação
│
├── services/                   # Microserviços (Docker)
│   ├── api/                    # API Gateway
│   ├── reports/                # Report Service
│   └── processors/             # Event Processors
│
├── rabbitmq_bus.py             # RabbitMQ Event Bus
├── game_monitor.py             # Pokemon Red Monitor
│
└── rom/                        # ROMs Game Boy
    └── Pokemon - Red Version.gb
```

---

## Conceitos Demonstrados

### Padrões Arquiteturais
- ✅ **Event-Driven Architecture**
- ✅ **Microservices Architecture**
- ✅ **Publish/Subscribe Pattern**
- ✅ **API Gateway Pattern**
- ✅ **Observer Pattern**

### Práticas de Engenharia
- ✅ **Separation of Concerns**
- ✅ **Loose Coupling**
- ✅ **High Cohesion**
- ✅ **Single Responsibility**
- ✅ **Containerization**
- ✅ **Horizontal Scalability**
- ✅ **Fault Tolerance**

---

## Troubleshooting

### RabbitMQ não conecta

```bash
# Aguardar RabbitMQ ficar saudável
docker compose logs rabbitmq | grep "Server startup complete"

# Reiniciar
docker compose restart rabbitmq
```

### Processadores não recebem eventos

```bash
# Verificar RabbitMQ Management UI
http://localhost:15672

# Reiniciar processadores
docker compose restart processor-battle processor-step
```

### Jogo não abre

```bash
# Verificar dependências
pip install pyboy pika

# Verificar ROM
ls rom/
```

---

## Licença

Este projeto é para fins educacionais, demonstrando arquitetura de microserviços e event-driven architecture.

**ROM do Pokemon Red não está incluída** - você deve fornecer sua própria ROM legalmente obtida.

---

## Referências

- [PyBoy Documentation](https://docs.pyboy.dk/)
- [RabbitMQ Tutorials](https://www.rabbitmq.com/getstarted.html)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Event-Driven Architecture](https://martinfowler.com/articles/201701-event-driven.html)
- [Microservices Patterns](https://microservices.io/patterns/microservices.html)

---

**Desenvolvido para demonstrar Arquitetura de Software Orientada a Eventos e Microserviços**
