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
            # inst.write("CH1:VOLT 5")
            # inst.write("CH1:CURR 1")
            # inst.write("OUTP CH1,ON")

            # volt = inst.query("CH1:VOLT?")
            # print(f"⚡ Voltaje CH1: {volt} V")

            break

    except Exception as e:
        print(f"{resource} -> ❌ Error: {e}")


import pyvisa

def configurar_medicion_ohm(resource_name="ASRL13::INSTR"):
    try:
        rm = pyvisa.ResourceManager()
        instrumento = rm.open_resource(resource_name)

        # Configuración básica para puerto serial (ajústala según el modelo del Fluke)
        instrumento.baud_rate = 9600
        instrumento.data_bits = 8
        instrumento.parity = pyvisa.constants.Parity.none
        instrumento.stop_bits = pyvisa.constants.StopBits.one
        instrumento.timeout = 2000  # 2 segundos

        # Limpia el buffer del instrumento
        instrumento.clear()

        # Comando SCPI para cambiar a modo de medición de resistencia (Ω)
        instrumento.write("FUNC 'RES'")  # Algunos modelos también aceptan "RES" o "MEAS:RES?"
        
        # Leer para confirmar cambio (puede variar según el modelo)
        respuesta = instrumento.query("FUNC?")
        print(f"Modo de medición actual: {respuesta.strip()}")

        instrumento.close()

    except Exception as e:
        print(f"Error al comunicar con el instrumento: {e}")

configurar_medicion_ohm()


