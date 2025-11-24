from pyboy import PyBoy
import time

CANDIDATES = {
    "Player X (D355)": 0xD355,
    "Player Y (D356)": 0xD356,
    "Player X (D361)": 0xD361,
    "Player Y (D362)": 0xD362,
    "Coord X (D360)": 0xD360,
    "Coord Y (D361)": 0xD361,
    "Map X (D4E6)": 0xD4E6,
    "Map Y (D4E7)": 0xD4E7,
}

print("🔍 Testando endereços de memória...")
print("Ande no jogo e veja quais valores mudam!\n")

pyboy = PyBoy(
    "rom/Pokemon - Red Version (USA, Europe) (SGB Enhanced).gb",
    window="SDL2",
    scale=3
)

previous_values = {}
frame_count = 0

try:
    while pyboy.tick():
        frame_count += 1

        if frame_count % 30 == 0:
            print(f"\n--- Frame {frame_count} ---")

            for name, addr in CANDIDATES.items():
                try:
                    value = pyboy.memory[addr]

                    if name in previous_values and previous_values[name] != value:
                        print(f"✓ {name}: {previous_values[name]} -> {value} (MUDOU!)")
                    else:
                        print(f"  {name}: {value}")

                    previous_values[name] = value
                except:
                    print(f"  {name}: ERRO ao ler")

except KeyboardInterrupt:
    print("\n\n🛑 Teste interrompido")

finally:
    pyboy.stop()
