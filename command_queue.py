"""
Command Queue - Fila FIFO para comandos do jogador.
Implementa padrão Producer-Consumer para Twitter Plays Pokemon.
"""

from queue import Queue, Empty
from typing import Optional


class CommandQueue:
    """
    Fila FIFO thread-safe para comandos do jogo.
    Permite que múltiplas threads adicionem comandos e o jogo os execute em ordem.
    """

    # Comandos válidos para Pokemon
    VALID_COMMANDS = {
        "up", "down", "left", "right",
        "a", "b",
        "start", "select"
    }

    def __init__(self, max_size: int = 100):
        """
        Args:
            max_size: Tamanho máximo da fila (evita spam)
        """
        self.queue = Queue(maxsize=max_size)
        self.command_count = 0

    def add_command(self, command: str) -> bool:
        """
        Adiciona um comando à fila FIFO.

        Args:
            command: Comando a ser executado ("up", "down", "a", "b", etc)

        Returns:
            True se comando foi adicionado, False se inválido ou fila cheia
        """
        command = command.lower().strip()

        # Validar comando
        if command not in self.VALID_COMMANDS:
            print(f"❌ Comando inválido: '{command}'")
            print(f"   Comandos válidos: {', '.join(sorted(self.VALID_COMMANDS))}")
            return False

        try:
            self.queue.put(command, block=False)
            self.command_count += 1
            print(f"✓ Comando '{command}' adicionado à fila (#{self.command_count})")
            return True
        except:
            print(f"⚠️  Fila cheia! Aguarde os comandos anteriores serem executados.")
            return False

    def get_next_command(self) -> Optional[str]:
        """
        Obtém o próximo comando da fila (FIFO).

        Returns:
            Próximo comando ou None se fila vazia
        """
        try:
            return self.queue.get(block=False)
        except Empty:
            return None

    def get_size(self) -> int:
        """Retorna o número de comandos na fila."""
        return self.queue.qsize()

    def is_empty(self) -> bool:
        """Verifica se a fila está vazia."""
        return self.queue.empty()

    def clear(self) -> None:
        """Limpa todos os comandos da fila."""
        while not self.queue.empty():
            try:
                self.queue.get(block=False)
            except Empty:
                break
        print("🗑️  Fila de comandos limpa!")
