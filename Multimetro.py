import pyvisa
import time
import re

def remove_duplicate(measurement):
    """
    Detecta y elimina valores duplicados de medición en la cadena.
    Por ejemplo: "+22.009E+3+22.009E+3" -> "+22.009E+3"
    """
    measurement = measurement.strip()
    
    # Usa una expresión regular para buscar valores tipo +22.009E+3
    pattern = r'[+-]?\d+\.\d+E[+-]?\d+'
    matches = re.findall(pattern, measurement)

    # Si hay al menos un valor, devuelve el primero
    if matches:
        return matches[0]

    # Si no encuentra ningún patrón, devuelve la cadena original
    return measurement

try:
    rm = pyvisa.ResourceManager()
    # Listamos los dispositivos conectados para verificar
    devices = rm.list_resources()
    print("Dispositivos conectados:", devices)
    
    # Abrimos el recurso del multímetro (ajusta si tu puerto es diferente)
    instrument = rm.open_resource('ASRL6::INSTR')
    
    # Configuramos parámetros de comunicación:
    instrument.baud_rate = 9600  # Asegúrate de que coincide con el multímetro
    instrument.timeout = 5000    # Timeout aumentado a 5000 ms
    
    # Cambiamos a la función de medición de voltaje
    instrument.write("VOLT")
    print("Multímetro cambiado a la función de voltaje (Volts).")
    
    # Esperamos unos segundos para que el cambio de función se estabilice
    time.sleep(2)
    
    # Obtenemos la medición usando VAL1?
    try:
        valor_medido = instrument.query("VAL1?")
        valor_medido = valor_medido.strip()
        #print("Valor medido (VAL1?):", valor_medido)
    except Exception as e:
        print("Error al obtener el valor medido con VAL1?:", e)
    
    # Obtenemos la medición usando MEAS1?
    try:
        valor_medido_meas = instrument.query("MEAS1?")
        valor_medido_meas = valor_medido_meas.strip()
        #print("Respuesta cruda (MEAS1?):", valor_medido_meas)
        
        # Procesamos la respuesta para eliminar la duplicación
        valor_corregido = remove_duplicate(valor_medido_meas)
        print("Valor de Voltaje:", valor_corregido)
    except Exception as e:
        print("Error al obtener el valor medido con MEAS1?: ", e)

except Exception as e:
    print("Error al conectar o comunicar con el multímetro: ", e)
