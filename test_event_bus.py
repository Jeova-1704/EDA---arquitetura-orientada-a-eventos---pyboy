from event_bus import EventBus


def test_event_bus():

    bus = EventBus()

    received_events = []

    def on_battle(data):
        print(f"✓ Evento de batalha recebido: {data}")
        received_events.append(("battle", data))

    def on_step(data):
        print(f"✓ Evento de passo recebido: {data}")
        received_events.append(("step", data))

    def on_generic(data):
        print(f"✓ Evento genérico recebido: {data}")
        received_events.append(("generic", data))

    print("\n1. Registrando subscribers...")
    bus.subscribe("battle", on_battle)
    bus.subscribe("step", on_step)
    bus.subscribe("generic", on_generic)
    print("   Subscribers registrados com sucesso!\n")

    print("2. Publicando eventos...")
    bus.publish("battle", {"battle_count": 1, "enemy": "Rattata"})
    bus.publish("step", {"step_count": 1, "direction": "up"})
    bus.publish("generic", {"message": "Evento de teste"})
    print()

    print("3. Testando múltiplos subscribers para o mesmo evento...")

    def on_battle_2(data):
        print(f"✓ Segundo subscriber de batalha recebeu: {data}")

    bus.subscribe("battle", on_battle_2)
    bus.publish("battle", {"battle_count": 2, "enemy": "Pidgey"})
    print()

    print("4. Testando unsubscribe...")
    bus.unsubscribe("battle", on_battle_2)
    bus.publish("battle", {"battle_count": 3, "enemy": "Caterpie"})
    print("   (Apenas o primeiro subscriber deve ter recebido)\n")

    print(f"5. Total de eventos processados: {len(received_events)}")
    print("   Eventos:", received_events)

    print("\n✅ Teste do Event Bus concluído com sucesso!")


if __name__ == "__main__":
    test_event_bus()
