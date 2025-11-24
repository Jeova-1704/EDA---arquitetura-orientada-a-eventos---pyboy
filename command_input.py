import threading
from command_queue import CommandQueue


class CommandInputHandler:

    def __init__(self, command_queue: CommandQueue):
        self.command_queue = command_queue
        self.running = False
        self.thread = None

    def start(self) -> None:
        if self.running:
            print("⚠️  Input handler já está rodando!")
            return

        self.running = True
        self.thread = threading.Thread(target=self._input_loop, daemon=True)
        self.thread.start()
        print("🎮 Input handler iniciado! Digite comandos no terminal.")

    def stop(self) -> None:
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        print("🛑 Input handler parado.")

    def _input_loop(self) -> None:
        print("\n" + "=" * 70)
        print("🎮 TWITTER PLAYS POKEMON - MODO COMANDOS ATIVADO")
        print("=" * 70)
        print("Digite comandos para controlar o jogo:")
        print("  - Movimento: up, down, left, right")
        print("  - Botões: a, b, start, select")
        print("  - Especiais: status, clear, quit")
        print("\nOs comandos serão executados em ordem (FIFO).")
        print("Digite 'help' para ver comandos disponíveis.")
        print("=" * 70 + "\n")

        while self.running:
            try:
                command = input(">>> ").strip().lower()

                if not command:
                    continue

                if command == "quit" or command == "exit":
                    print("👋 Encerrando jogo...")
                    self.running = False
                    break

                elif command == "help":
                    self._show_help()

                elif command == "status":
                    self._show_status()

                elif command == "clear":
                    self.command_queue.clear()

                else:
                    commands = command.split()
                    for cmd in commands:
                        self.command_queue.add_command(cmd)

            except EOFError:
                break
            except KeyboardInterrupt:
                print("\n⚠️  Interrompido pelo usuário")
                break
            except Exception as e:
                print(f"❌ Erro ao processar comando: {e}")

    def _show_help(self) -> None:
        print("\n📖 COMANDOS DISPONÍVEIS:")
        print("\n🎮 Controles do Jogo:")
        print("  up, down, left, right  - Movimento")
        print("  a, b                   - Botões A e B")
        print("  start, select          - Start e Select")
        print("\n⚙️  Comandos Especiais:")
        print("  status                 - Mostra status da fila")
        print("  clear                  - Limpa fila de comandos")
        print("  help                   - Mostra esta ajuda")
        print("  quit / exit            - Encerra o jogo")
        print("\n💡 Dica: Você pode enviar vários comandos de uma vez:")
        print("  Exemplo: up up right a")
        print()

    def _show_status(self) -> None:
        size = self.command_queue.get_size()
        print(f"\n📊 STATUS DA FILA:")
        print(f"  Comandos na fila: {size}")
        print(f"  Total processados: {self.command_queue.command_count}")
        print()
