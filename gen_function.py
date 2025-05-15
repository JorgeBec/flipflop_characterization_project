import pyvisa
import time

# Inicializar el administrador de recursos
rm = pyvisa.ResourceManager()

# Conectar al generador (ajusta si no es ASRL6)
gen = rm.open_resource('ASRL6::INSTR')

# Configurar comunicación serie
gen.baud_rate = 9600
gen.data_bits = 8
gen.parity = pyvisa.constants.Parity.none
gen.stop_bits = pyvisa.constants.StopBits.one
gen.write_termination = '\r\n'
gen.read_termination = '\r\n'
gen.timeout = 3000  # milisegundos

# Solicitar al usuario los parámetros del barrido
inicio = int(input("Frecuencia inicial (Hz): "))
fin = int(input("Frecuencia final (Hz): "))
paso = int(input("Incremento (Hz): "))

try:
    print("Iniciando barrido de frecuencia...\n")
    for f in range(inicio, fin + 1, paso):
        print(f"Estableciendo frecuencia: {f} Hz")
        gen.write(f"SOUR1:FREQ {f}")
        time.sleep(0.5)

        # Consultar para confirmar
        respuesta = gen.query("SOUR1:FREQ?")
        print(f"Frecuencia confirmada: {respuesta.strip()} Hz\n")

        # Esperar 2 segundos antes del siguiente paso
        time.sleep(2)

except Exception as e:
    print("Error durante el barrido:", e)

finally:
    gen.close()
    print("Conexión cerrada.")