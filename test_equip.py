import pyvisa

rm = pyvisa.ResourceManager()
resources = rm.list_resources()

# Buscar automáticamente la fuente Siglent
for resource in resources:
    try:
        inst = rm.open_resource(resource, timeout=3000)
        inst.write_termination = '\n'
        inst.read_termination = '\n'

        idn = inst.query("*IDN?").strip()
        print(f"{resource} -> {idn}")

        if "SPD" in idn or "Siglent" in idn:
            print("✅ Fuente SPD3303X-E detectada. Conectando...")
            
            # Ejemplo de comandos
            inst.write("CH1:VOLT 5")
            inst.write("CH1:CURR 1")
            inst.write("OUTP CH1,ON")

            volt = inst.query("CH1:VOLT?")
            print(f"⚡ Voltaje CH1: {volt} V")

            break

    except Exception as e:
        print(f"{resource} -> ❌ Error: {e}")
