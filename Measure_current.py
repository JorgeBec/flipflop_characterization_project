import nidaqmx

# Pedir valores al usuario
v_ao0 = float(input("Ingresa el voltaje para ao0 (0 a 5V): "))
v_ao1 = float(input("Ingresa el voltaje para ao1 (0 a 5V): "))
p01_state = input("¿Quieres que p0.1 esté en True o False? (true/false): ").strip().lower() == "true"

# Validar rangos
if not (0 <= v_ao0 <= 5 and 0 <= v_ao1 <= 5):
    print("Error: Los voltajes deben estar entre 0 y 5V.")
    exit()

# Crear la tarea para las salidas analógicas y digitales
with nidaqmx.Task() as task_ao, nidaqmx.Task() as task_do:
    # Configurar salidas analógicas
    task_ao.ao_channels.add_ao_voltage_chan("Dev1/ao0", min_val=0.0, max_val=5.0)
    task_ao.ao_channels.add_ao_voltage_chan("Dev1/ao1", min_val=0.0, max_val=5.0)
    
    # Escribir valores analógicos
    task_ao.write([v_ao0, v_ao1])
    
    # Configurar salida digital correctamente
    task_do.do_channels.add_do_chan("Dev1/port0/line1")  # Ajuste del nombre del canal
    
    # Escribir valor digital
    task_do.write(p01_state)

print(f"Voltajes aplicados: ao0 = {v_ao0}V, ao1 = {v_ao1}V")
print(f"Estado de p0.1: {'True' if p01_state else 'False'}")
