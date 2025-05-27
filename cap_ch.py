import pyvisa
import numpy as np
import pandas as pd
import re
import matplotlib.pyplot as plt

rm = pyvisa.ResourceManager()
devices = rm.list_resources()


## -------------------------------- Oscilloscope setup ------------------------------------------------- ##
def detect_tektronix_oscilloscope():
    rm = pyvisa.ResourceManager()
    resources = rm.list_resources()
    tektronix_pattern = re.compile(r"TEKTRONIX,TDS", re.IGNORECASE)

    for resource in resources:
        try:
            instrument = rm.open_resource(resource)
            instrument.timeout = 3000
            idn = instrument.query("*IDN?").strip()
            print(f"Checking: {idn}")  # Opcional
            if tektronix_pattern.search(idn):
                return instrument
        except Exception as e:
            print(f"Error with {resource}: {e}")
            continue
    return None


osc = detect_tektronix_oscilloscope()
if osc:
    print("Osciloscopio detectado:", osc.query("*IDN?"))
else:
    print("No se detectó el osciloscopio Tektronix.")

## -----------------------------------Power supply configuration ---------------------------------------------------------------
def capture_channel(channel):
    # Set up for selected channel
    osc.write(f"DATa:SOU CH{channel}")
    osc.write("DATa:ENCdg SRIBinary")
    osc.write("DATa:WIDth 2")
    osc.write("DATa:STARt 1")
    osc.write("DATa:STOP 2500")


    # Get scale factors
    x_increment = float(osc.query("WFMPRE:XINcr?"))
    x_origin = float(osc.query("WFMPRE:XZERO?"))
    y_increment = float(osc.query("WFMPRE:YMUlt?"))
    y_origin = float(osc.query("WFMPRE:YZEro?"))
    y_offset = float(osc.query("WFMPRE:YOFF?"))

    # Read waveform
    raw_data = osc.query_binary_values("CURVe?", datatype='h', container=np.array)
    voltages = (raw_data - y_offset) * y_increment + y_origin
    time = np.arange(len(voltages)) * x_increment + x_origin

    return time, voltages