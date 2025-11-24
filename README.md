# Pokemon Red - Event-Driven Architecture

Sistema de monitoramento e controle para Pokemon Red implementando arquitetura orientada a eventos com padrão Publish/Subscribe usando PyBoy emulator.

## Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Requisitos Implementados](#requisitos-implementados)
- [Quick Start](#quick-start)
- [Arquitetura](#arquitetura)
- [Modos de Execução](#modos-de-execução)
- [Componentes do Sistema](#componentes-do-sistema)
- [Controles e Comandos](#controles-e-comandos)
- [Testes](#testes)
- [Docker e Containerização](#docker-e-containerização)
- [Troubleshooting](#troubleshooting)
- [Conceitos Demonstrados](#conceitos-demonstrados)
- [Referências](#referências)

---

## Sobre o Projeto

Este projeto implementa uma **arquitetura orientada a eventos (Event-Driven Architecture)** para Pokemon Red usando o emulador PyBoy. Inspirado no "Twitter Plays Pokemon", o sistema detecta eventos do jogo em tempo real e mantém estatísticas detalhadas através de processadores de eventos independentes.

### Tecnologias

- **Python 3.12+**
- **PyBoy 2.6.1+** - Emulador Game Boy
- **RabbitMQ 3.12** - Message broker (modo distribuído)
- **Docker & Docker Compose** - Containerização
- **pika** - Cliente RabbitMQ para Python

---

## Requisitos Implementados

- ✅ **Ponto 1**: Event Bus (Publish/Subscribe)
- ✅ **Ponto 2**: 6 Processadores de Eventos
- ✅ **Ponto 3**: Integração com PyBoy + Relatórios periódicos
- ✅ **Ponto 4**: Controle FIFO via comandos (Twitter Plays Pokemon)
- ✅ **Ponto 5**: RabbitMQ como broker externo
- ⚙️ **Ponto 6**: Docker Compose (em desenvolvimento)

---

## Quick Start

### Instalação

```bash
# Instalar dependências usando uv
uv sync

# OU usando pip
pip install pyboy pika
```

### Adicionar ROM

Coloque o arquivo ROM do Pokemon Red na pasta `rom/`:
```
rom/Pokemon - Red Version (USA, Europe) (SGB Enhanced).gb
```

### Executar

**Modo Normal (Teclado):**
```bash
python main.py
```

**Modo FIFO (Comandos):**
```bash
python main_fifo.py
```

**Modo Broker (RabbitMQ):**
```bash
# 1. Iniciar RabbitMQ
docker-compose up -d

# 2. Executar jogo
python main_broker.py

# 3. Monitorar (opcional)
# http://localhost:15672 (pokemon/pokemon123)
```

---

## Arquitetura

### Visão Geral

```
┌─────────────────────────────────────────────────────────────────┐
│                         CAMADA DE JOGO                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              PyBoy (Emulador Game Boy)                   │   │
│  │  - Memória (RAM/ROM)                                     │   │
│  │  - CPU Z80                                               │   │
│  │  - Display (SDL2)                                        │   │
│  └────────────────────┬─────────────────────────────────────┘   │
└─────────────────────────┼───────────────────────────────────────┘
                          │ Leitura de memória
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CAMADA DE MONITORAMENTO                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           PokemonRedMonitor (game_monitor.py)            │   │
│  │  - Lê endereços de memória a cada frame                 │   │
│  │  - Detecta mudanças (posição, HP, batalhas)             │   │
│  │  - Publica eventos quando detecta mudanças              │   │
│  └────────────────────┬─────────────────────────────────────┘   │
└─────────────────────────┼───────────────────────────────────────┘
                          │ Publica eventos
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CAMADA DE COMUNICAÇÃO                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │               Event Bus / RabbitMQ                       │   │
│  │  - Gerencia subscribers                                  │   │
│  │  - Roteia eventos para callbacks                        │   │
│  │  - Desacopla publishers de subscribers                  │   │
│  └────────────────────┬─────────────────────────────────────┘   │
└─────────────────────────┼───────────────────────────────────────┘
                          │ Notifica subscribers
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                  CAMADA DE PROCESSAMENTO                        │
│  ┌──────────────┬──────────────┬──────────────┬─────────────┐   │
│  │ BattleCounter│  StepCounter │PositionTrack│ TimeTracker │   │
│  ├──────────────┼──────────────┼──────────────┼─────────────┤   │
│  │HealthTracker │ReportGenerat.│  ... outros processadores │   │
│  └──────────────┴──────────────┴──────────────┴─────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Padrões Arquiteturais

#### 1. Event-Driven Architecture (EDA)
Sistema baseado em eventos onde componentes se comunicam através de mensagens assíncronas.

#### 2. Publish/Subscribe Pattern
Event Bus implementa padrão Pub/Sub onde:
- **Publishers** emitem eventos sem conhecer os subscribers
- **Subscribers** se registram para eventos específicos
- **Event Bus** gerencia e roteia as mensagens

#### 3. Observer Pattern
Processadores de eventos atuam como observers que reagem a mudanças de estado do jogo.

#### 4. Producer-Consumer Pattern (Modo FIFO)
Thread de input produz comandos → Fila FIFO → Main loop consome comandos

---

## Modos de Execução

### Comparação Rápida

| Modo | Arquivo | Controle | Event Bus | Ponto | Complexidade |
|------|---------|----------|-----------|-------|--------------|
| **Normal** | `main.py` | Teclado (SDL2) | Local (memória) | 1-3 | ⭐ Básico |
| **FIFO** | `main_fifo.py` | Comandos (texto) | Local (memória) | 4 | ⭐⭐ Médio |
| **Broker** | `main_broker.py` | Teclado (SDL2) | RabbitMQ (externo) | 5 | ⭐⭐⭐ Avançado |

### 1. Modo Normal - Controle via Teclado

**Características:**
- ✅ Controle via teclado (setas, Z, X, Enter)
- ✅ Event Bus local (em memória)
- ✅ 6 processadores de eventos
- ✅ Relatórios periódicos e finais

**Executar:**
```bash
python main.py
```

**Controles:**
- **Setas**: Movimento
- **Z**: Botão A (Confirmar/Interagir)
- **X**: Botão B (Cancelar/Correr)
- **Enter**: Start (Menu)
- **Backspace**: Select
- **ESC**: Fechar jogo

### 2. Modo FIFO - Twitter Plays Pokemon

**Características:**
- ✅ Controle via comandos de texto
- ✅ Fila FIFO thread-safe
- ✅ Delay controlado (250ms entre comandos)
- ✅ Thread separada para input
- ✅ Simula múltiplos jogadores

**Executar:**
```bash
python main_fifo.py
```

**Comandos:**
```bash
# Movimento
>>> up up down left right

# Botões
>>> a b start select

# Especiais
>>> status   # Ver fila
>>> clear    # Limpar fila
>>> help     # Ajuda
>>> quit     # Sair
```

**Arquitetura:**
```
Terminal → CommandQueue (FIFO) → Main Loop → PyBoy
              ↑                       ↓
     InputThread              Event Bus → Processors
```

### 3. Modo Broker - Arquitetura Distribuída

**Características:**
- ✅ RabbitMQ como broker externo
- ✅ Mensagens persistentes
- ✅ Arquitetura distribuída
- ✅ Interface web de monitoramento
- ✅ Escalabilidade horizontal

**Executar:**
```bash
# 1. Iniciar RabbitMQ
docker-compose up -d

# 2. Aguardar 10-15 segundos

# 3. Executar jogo
python main_broker.py

# 4. Monitorar (opcional)
# http://localhost:15672
# Username: pokemon
# Password: pokemon123
```

**Arquitetura:**
```
Monitor → RabbitMQ (servidor externo) → Consumers (threads)
                ↓
          Exchange (topic)
                ↓
    ┌──────────┼──────────┬──────────┐
    ▼          ▼          ▼          ▼
  Queue 1   Queue 2   Queue 3    Queue N
    ↓          ▼          ▼          ↓
Processor1 Processor2 Processor3  ...
 (thread)   (thread)   (thread)
```

---

## Componentes do Sistema

### 1. Event Bus (`event_bus.py`)

**Responsabilidade:** Broker central de mensagens

**API:**
```python
event_bus.subscribe(event_type, callback)  # Registra subscriber
event_bus.publish(event_type, data)        # Publica evento
event_bus.unsubscribe(event_type, callback) # Remove subscriber
```

**Características:**
- Thread-safe
- O(1) para adicionar subscriber
- O(n) para publicar evento

### 2. Game Monitor (`game_monitor.py`)

**Responsabilidade:** Detectar eventos do jogo lendo memória

**Funcionamento:**
1. Chamado a cada frame (60 FPS)
2. Lê endereços específicos da memória
3. Compara com estado anterior
4. Se detectar mudança, publica evento

**Endereços Monitorados:**
```python
0xD362  # Player X position
0xD361  # Player Y position
0xD057  # In battle flag
0xD35E  # Current map ID
0xD52A  # Player direction
0xD015-0xD016  # Current HP (2 bytes)
0xD018-0xD019  # Max HP (2 bytes)
```

### 3. Event Processors (`event_processors.py`)

#### 3.1 BattleCounter
- **Evento:** `battle_start`
- **Função:** Conta batalhas e mantém histórico

#### 3.2 StepCounter
- **Evento:** `step`
- **Função:** Conta passos do jogador
- **Output:** Mostra a cada 10 passos

#### 3.3 PositionTracker
- **Evento:** `position_change`
- **Função:** Rastreia posição e mapa

#### 3.4 TimeTracker
- **Eventos:** `game_start`, `game_pause`, `game_resume`
- **Função:** Rastreia tempo de jogo
- **Cálculo:** Tempo real - tempo pausado

#### 3.5 HealthTracker
- **Evento:** `health_change`
- **Função:** Monitora HP do Pokémon
- **Alerta:** HP < 20%

#### 3.6 ReportGenerator
- **Eventos:** `game_end`, timer interno
- **Função:** Gera relatórios periódicos (5min) e finais
- **Saída:** Relatório formatado no console

### 4. RabbitMQ Event Bus (`rabbitmq_bus.py`)

**Responsabilidade:** Wrapper para RabbitMQ mantendo mesma API

**Características:**
- Conecta via protocolo AMQP
- Exchange tipo topic
- Consumer thread por evento
- Serialização JSON
- Message acknowledgements

---

## Controles e Comandos

### Modo Normal - Teclado

| Tecla | Função | Descrição |
|-------|--------|-----------|
| **↑↓←→** | Movimento | Move o personagem |
| **Z** | Botão A | Confirmar / Interagir |
| **X** | Botão B | Cancelar / Correr |
| **Enter** | START | Abrir menu |
| **Backspace** | SELECT | Alternar Pokémons |
| **ESC** | - | Fechar jogo |

### Modo FIFO - Comandos

**Comandos de Movimento:**
```bash
up, down, left, right
```

**Comandos de Botões:**
```bash
a, b, start, select
```

**Comandos Especiais:**
```bash
status  # Mostra status da fila
clear   # Limpa fila de comandos
help    # Mostra ajuda
quit    # Encerra o jogo
```

**Exemplos:**
```bash
# Andar e interagir
>>> up up up right a

# Ver status
>>> status
📊 STATUS DA FILA:
  Comandos na fila: 3
  Total processados: 47

# Limpar fila
>>> clear
🗑️  Fila de comandos limpa!

# Sair
>>> quit
```

### Contextos de Jogo

**No Overworld (Mundo Aberto):**
- Movimento: `up, down, left, right`
- Interagir com NPC: `a`
- Abrir menu: `start`
- Correr: `b + movimento`

**Em Batalha:**
- Atacar: `a a`
- Selecionar movimento: `a down a`
- Usar item: `down right a`
- Fugir: `down down down a`

**Em Menus:**
- Navegar: `up, down, left, right`
- Selecionar: `a`
- Voltar: `b`

---

## Testes

### Testar Event Bus

```bash
python test_event_bus.py
```

**Saída esperada:**
```
1. Registrando subscribers...
   ✅ Subscribers registrados com sucesso!

2. Publicando eventos...
   ⚔️  Evento de batalha recebido: {'battle_count': 1}
   👣 Evento de passo recebido: {'step_count': 1}

✅ Teste do Event Bus concluído com sucesso!
```

### Testar Modo FIFO

```bash
python main_fifo.py
>>> up up right a
>>> status
>>> quit
```

### Testar RabbitMQ

```bash
# 1. Iniciar RabbitMQ
docker-compose up -d

# 2. Verificar se está rodando
docker ps

# 3. Executar jogo
python main_broker.py

# 4. Verificar interface web
# http://localhost:15672
# Login: pokemon / pokemon123
```

---

## Docker e Containerização

### Arquitetura Docker

```
┌────────────────────────────────────────────┐
│  Container: rabbitmq                       │
│  - Image: rabbitmq:3.12-management-alpine  │
│  - Ports: 5672, 15672                      │
└────────────────┬───────────────────────────┘
                 │
    ┌────────────┼────────────┬──────────┐
    ▼            ▼            ▼          ▼
┌──────────┬──────────┬──────────┬──────────┐
│processor │processor │processor │processor │
│ -battle  │ -step    │ -health  │ -time    │
└──────────┴──────────┴──────────┴──────────┘
```

### Comandos Docker

**Build:**
```bash
# Build todas imagens
docker-compose build

# Build sem cache
docker-compose build --no-cache
```

**Executar:**
```bash
# Iniciar todos (background)
docker-compose up -d

# Iniciar e ver logs
docker-compose up

# Escalar serviço
docker-compose up -d --scale processor-step=3
```

**Gerenciar:**
```bash
# Ver status
docker-compose ps

# Ver logs
docker-compose logs -f

# Parar
docker-compose down

# Parar e remover volumes
docker-compose down -v
```

**Monitorar:**
```bash
# Ver uso de recursos
docker stats

# Ver logs de serviço específico
docker logs pokemon-processor-step

# Entrar em container
docker exec -it pokemon-rabbitmq /bin/sh
```

### Escalabilidade

```bash
# Escalar para 3 instâncias
docker-compose up -d --scale processor-step=3
```

RabbitMQ faz load balancing automático entre os consumers!

---

## Troubleshooting

### Problema: "ROM não encontrado"

**Solução:**
```bash
# Verificar se ROM está no local correto
ls rom/

# Deve ter:
# Pokemon - Red Version (USA, Europe) (SGB Enhanced).gb
```

### Problema: RabbitMQ não conecta

**Sintomas:**
```
❌ Não foi possível conectar ao RabbitMQ
```

**Solução:**
```bash
# 1. Verificar se está rodando
docker ps | grep rabbitmq

# 2. Iniciar se não estiver
docker-compose up -d

# 3. Aguardar 15 segundos
sleep 15

# 4. Tentar novamente
python main_broker.py
```

### Problema: Porta já em uso

**Sintomas:**
```
Error: port 5672 already in use
```

**Solução:**
```bash
# Ver processos na porta
netstat -ano | findstr :5672

# Parar containers
docker-compose down

# Reiniciar
docker-compose up -d
```

### Problema: Container não inicia

**Solução:**
```bash
# Ver logs
docker logs <container-name>

# Ver erro detalhado
docker-compose logs -f

# Recriar containers
docker-compose down
docker-compose up -d
```

### Problema: Comandos FIFO não executam

**Verificações:**
1. ✅ PyBoy inicializado com `no_input=True`?
2. ✅ CommandQueue criada?
3. ✅ InputHandler iniciado?
4. ✅ Comandos válidos?

**Debug:**
```bash
# Ver mensagens de erro
# no console onde rodou main_fifo.py

# Testar comando simples
>>> up
```

---

## Conceitos Demonstrados

### Padrões de Projeto
- ✅ Event-Driven Architecture
- ✅ Publish/Subscribe Pattern
- ✅ Observer Pattern
- ✅ Producer-Consumer Pattern

### Boas Práticas
- ✅ Separation of Concerns
- ✅ Loose Coupling
- ✅ Open/Closed Principle
- ✅ Single Responsibility Principle
- ✅ Thread Safety

### Conceitos de Sistema
- ✅ Event Bus
- ✅ Fila FIFO
- ✅ Threading
- ✅ Memory Mapping
- ✅ Real-time Monitoring
- ✅ Message Broker (RabbitMQ)
- ✅ Containerização (Docker)

---

## Referências

- [PyBoy Documentation](https://docs.pyboy.dk/)
- [Pokemon Red Memory Map](https://datacrystal.romhacking.net/wiki/Pok%C3%A9mon_Red/Blue:RAM_map)
- [Event-Driven Architecture](https://martinfowler.com/articles/201701-event-driven.html)
- [RabbitMQ Tutorials](https://www.rabbitmq.com/getstarted.html)
- [Docker Documentation](https://docs.docker.com/)

---

## Estrutura de Arquivos

```
pokemon/
├── main.py                 # Modo normal (teclado)
├── main_fifo.py           # Modo FIFO (comandos)
├── main_broker.py         # Modo broker (RabbitMQ)
├── event_bus.py           # Event Bus local
├── rabbitmq_bus.py        # RabbitMQ Event Bus
├── event_processors.py    # 6 processadores
├── game_monitor.py        # Monitor do jogo
├── command_queue.py       # Fila FIFO
├── command_input.py       # Input handler
├── test_event_bus.py      # Testes
├── docker-compose.yml     # Docker orchestration
├── Dockerfile             # Container image
├── pyproject.toml         # Dependências
└── rom/                   # ROMs do Game Boy
    └── Pokemon - Red Version.gb
```

---

## Exemplo de Relatório

```
======================================================================
📊 RELATÓRIO PERIÓDICO #1
⏰ Gerado em: 2024-11-23 15:30:45
======================================================================

⏱️  TEMPO DE JOGO
   Tempo total: 00:05:23
   Iniciado em: 2024-11-23 15:25:22

👣 PASSOS
   Total de passos: 147

⚔️  BATALHAS
   Total de batalhas: 3

📍 POSIÇÃO ATUAL
   Posição: (10, 15)
   Mapa: 1

❤️  SAÚDE
   HP: 18/22 (81.8%)

======================================================================
```

---

## Licença

Projeto educacional para disciplina de Arquitetura de Software.

---

## Contribuindo

### Adicionar Novo Processador

1. Criar classe em `event_processors.py`:
```python
class NewProcessor:
    def on_new_event(self, data):
        # Processar evento
        pass

    def get_stats(self):
        return {"stat": value}
```

2. Registrar em `main.py`:
```python
new_proc = NewProcessor()
processors["new"] = new_proc
event_bus.subscribe("new_event", new_proc.on_new_event)
```

3. Adicionar ao relatório (opcional):
```python
# Em ReportGenerator.generate_report()
stats = self.processors["new"].get_stats()
print(f"Nova Stat: {stats['stat']}")
```

### Adicionar Novo Evento

1. Publicar do monitor:
```python
# Em PokemonRedMonitor.update()
if self.detect_new_condition():
    self.event_bus.publish("new_event", {"data": value})
```

2. Criar/usar processador para reagir

---

**Desenvolvido com ❤️ para aprendizado de Arquitetura de Software**
