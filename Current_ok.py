# -*- coding: utf-8 -*-
"""
Created on Sat May 24 17:07:43 2025

@author: Greta
"""

import pyvisa
import nidaqmx
from nidaqmx.constants import LineGrouping
import time
import re
from tabulate import tabulate

Measurement_1 = None
Measurement_2 = None
Measurement_3 = None
Measurement_4 = None

#-----------------------------------Power supply configuration ---------------------------------------------------------------
def detect_siglent_power_supply():
    rm = pyvisa.ResourceManager()
    for resource in rm.list_resources():
        try:
            instrument = rm.open_resource(resource)
            idn = instrument.query("*IDN?")
            if "SIGLENT" in idn.upper() and "SPD3303X-E" in idn.upper():
                return instrument
        except Exception as e:
            print(f"Error with {resource}: {e}")
            continue
    return None

# -------------------------------- Fluke 45 Multimeter configuration ----------------------------------------------------
def remove_duplicate(measurement):
    pattern = r'[+-]?\d+\.\d+E[+-]?\d+'
    matches = re.findall(pattern, measurement.strip())
    return matches[0] if matches else measurement

def read_voltage_fluke45(port='ASRL4::INSTR'): 
    try:
        rm = pyvisa.ResourceManager()
        multimeter = rm.open_resource(port)
        multimeter.baud_rate = 9600
        multimeter.timeout = 5000
        multimeter.write("VOLT")
        time.sleep(2)

        try:
            multimeter.query("VAL1?")
        except:
            pass 

        try:
            meas = multimeter.query("MEAS1?")
            return float(remove_duplicate(meas))
        except Exception as e:
            print("Error in MEAS1?:", e)
            return None
    except Exception as e:
        print("Error communicating with Fluke 45:", e)
        return None

def safe_voltage_read_fluke45(max_attempts=3, min_v=0.0, max_v=6.0):
    for attempt in range(max_attempts):
        voltage = read_voltage_fluke45()
        if voltage is not None and min_v <= voltage <= max_v:
            return voltage
        print(f"Warning: Invalid voltage reading ({voltage}), retrying ({attempt+1}/{max_attempts})...")
        time.sleep(0.5)
    print("Failed to get a valid voltage after retries.")
    return None

# --------------------------------- Daq configuration for multiplexer -------------------------------------------
        #La linea 0 al pin 9 (C) 
        #La linea 1 al pin 10 (B) 
        #La linea 2 al pin 11 (A)

    #       C      B       A
Canal_0 = [False, False, False] 
Canal_1 = [False, False, True]  
Canal_2 = [False, True, False] 
Canal_3 = [False, True, True] 
Canal_4 = [True, False, False] 
Canal_5 = [True, False, True] 
Canal_6 = [True, True, False]
Canal_7 = [True, True, True]

# --------------------------------- Daq-------------------------------------------
with nidaqmx.Task() as task_ao, nidaqmx.Task() as task_do, nidaqmx.Task() as do_task:
    task_ao.ao_channels.add_ao_voltage_chan("Dev2/ao0", min_val=0.0, max_val=5.0)
    task_ao.ao_channels.add_ao_voltage_chan("Dev2/ao1", min_val=0.0, max_val=5.0)

    task_do.do_channels.add_do_chan("Dev2/port0/line0:2", line_grouping=LineGrouping.CHAN_PER_LINE)
    do_task.do_channels.add_do_chan("Dev2/port1/line0")
    do_task.do_channels.add_do_chan("Dev2/port1/line1")

    Voltage_1 = detect_siglent_power_supply()
    if Voltage_1:
        Voltage_1.write("OUTP CH1,OFF")
        Voltage_1.write("OUTP CH2,OFF")
        time.sleep(3)
        Voltage_1.write("CH1:VOLT 5")
        Voltage_1.write("CH2:VOLT 5")
        Voltage_1.write("CH1:CURR 0.5")
        Voltage_1.write("CH2:CURR 0.5")
        Voltage_1.write("OUTP CH1,ON")
        Voltage_1.write("OUTP CH2,ON")
    else:
        print("Power supply not detected.")

    time.sleep(3)
    #---------------------------------------------------Voltage1------------------------------------------
    task_ao.write([5, 0])
    task_do.write(Canal_0)
    do_task.write([True, True])
    time.sleep(3)

    do_task.write([True, False])
    time.sleep(3)

    Measurement_1 = safe_voltage_read_fluke45()
    print(f"Measurement 1: {Measurement_1} V")

    time.sleep(3)
 #---------------------------------------------------Voltage2------------------------------------------

    task_do.write(Canal_3)
    time.sleep(3)

    Measurement_2 = safe_voltage_read_fluke45()
    print(f"Measurement 2: {Measurement_2} V")

    time.sleep(3)

    resistance = 1  
    if Measurement_1 is not None and Measurement_2 is not None:
        Icc = (Measurement_1 - Measurement_2) / resistance
        print(f"Icc = {Icc:.6e} A")
    else:
        print("No se pudo calcular Icc porque alguna medición falló.")
    
    #----------------------------------------------------Voltage3--------------------------------------------------
    task_ao.write([0, 5])
 
    task_do.write(Canal_2)
    do_task.write([True, True])
    time.sleep(20)

    do_task.write([True, False])
    time.sleep(3)

    Measurement_3 = safe_voltage_read_fluke45()
    if Measurement_3 is not None:
        print(f"Measurement 3: {Measurement_3} V")
    else:
        print("Measurement 3 failed!")

    time.sleep(3)
    

    #-----------------------------------------------Voltage4---------------------------------------------------------
    task_do.write(Canal_1)
    time.sleep(20)

    Measurement_4 = safe_voltage_read_fluke45()
    if Measurement_4 is not None:
        print(f"Measurement 4: {Measurement_4} V")
    else:
        print("Measurement 4 failed!")

    time.sleep(3)
    
    Voltage_1.write("OUTP CH1,OFF")
    Voltage_1.write("OUTP CH2,OFF")
    resistance = 1 
    # Verificar si todas las mediciones fueron exitosas antes de calcular I_IL
    if Measurement_3 is not None and Measurement_4 is not None:
        I_IL = (Measurement_3 - Measurement_4) / resistance
        print(f"I_IL = {I_IL:.6e} A")
    else:
        print("I_IL could not be calculated because some measurement failed")
        
        
        tabla_resultados = [
    ["ICC", f"{Icc:.6e}" if Measurement_1 is not None and Measurement_2 is not None else "N/A"],
    ["IIL", f"{I_IL:.6e}" if Measurement_3 is not None and Measurement_4 is not None else "N/A"]
]

print(tabulate(tabla_resultados, headers=["Current", "Result"], tablefmt="grid"))
