import pyvisa
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

rm = pyvisa.ResourceManager()
devices = rm.list_resources()

osc = rm.open_resource(devices[1])
print(osc.query("*IDN?"))


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