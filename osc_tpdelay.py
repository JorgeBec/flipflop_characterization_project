import pyvisa
import nidaqmx
import numpy as np
import time
import pandas as pd
import matplotlib.pyplot as plt
from daq_setup import initialize_daq_outputs_zero

rm = pyvisa.ResourceManager()
devices = rm.list_resources()

osc = rm.open_resource(devices[0])

#initialize_daq_outputs_zero("Dev1")


### -- User inputs -- ###

#vcc_user = float(input("Vcc = "))
#freq_user = float(input("f = "))

### -- display set -- ###
osc.write("horizontal:main:scale 10E-9")
osc.write("HORizontal:POSition 0")
osc.write("HORizontal:POSition 20E-9")

osc.write("CH1:SCAle 1") 
osc.write("CH2:SCAle 1") 

osc.write("CH1:POSition -3")
osc.write("CH2:POSition -3")

osc.write("TRIGGER:MAIN:MODE NORMAL")
osc.write("TRIGger:MAIn:EDGE:SLOpe FALL")
osc.write("TRIGger:MAIn:EDGE:SOUrce CH1")


##DAQ
with nidaqmx.Task() as task:
    task.ao_channels.add_ao_voltage_chan("Dev1/ao0", min_val=0, max_val=5)
    task.ao_channels.add_ao_voltage_chan("Dev1/ao1", min_val=0, max_val=5)
    task.write([4.5, 4.5])  # Write voltages to ao0 and ao1 simultaneously

##DAQ
# clock flank down
with nidaqmx.Task() as task:
    task.do_channels.add_do_chan("Dev1/port1/line3")
    task.write(True)  # Write voltages to ao0 and ao1 simultaneously
    time.sleep(0.1)  # Wait for 100 ms
    task.write(False)  # Write voltages to ao0 and ao1 simultaneously

time.sleep(0.1)  # Wait for 100 ms






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
    print(raw_data)
    voltages = (raw_data - y_offset) * y_increment + y_origin
    print(voltages)
    time = np.arange(len(voltages)) * x_increment + x_origin

    return time, voltages

# Capture both channels
time1, volts1 = capture_channel(1)
print("array with voltages of ch1: ",volts1)
print("array with voltages of ch1: ",time1)
time2, volts2 = capture_channel(2)
print("array with voltages of ch2: ",volts2)
print("array with voltages of ch2: ",time2)

# Create and save DataFrame
df = pd.DataFrame({
    "Time (s)": time1,
    "Voltage (V)": volts1
})
df.to_csv("channel1_capture.csv", index=False)


# Create and save DataFrame 2
df = pd.DataFrame({
    "Time (s)": time2,
    "Voltage (V)": volts2
})
df.to_csv("channel2_capture.csv", index=False)

### Find the propagation delay between two channels

def find_crossing_time(time, voltages, threshold):
    """
    Find the time when the waveform first reaches or exceeds the threshold.
    No interpolation is used.
    """
    for i in range(len(voltages)):
        if voltages[i] >= threshold:
            return time[i]
    return None  # No crossing found

# Assuming time1, volts1 and time2, volts2 were captured from previous example

# Define threshold voltage (50% of amplitude)
threshold_ch1 = (np.max(volts1) + np.min(volts1)) / 2
print("threshold_ch1", threshold_ch1)

threshold_ch2 = (np.max(volts2) + np.min(volts2)) / 2
print("threshold_c2", threshold_ch2) 
      
# Find crossing times for rising edge
cross_time_ch1 = find_crossing_time(time1, volts1, threshold_ch1)
print("cross_time_ch1", cross_time_ch1)
cross_time_ch2 = find_crossing_time(time2, volts2, threshold_ch2)
print("cross_time_ch2", cross_time_ch2)

if cross_time_ch1 is not None and cross_time_ch2 is not None:
    propagation_delay = cross_time_ch2 - cross_time_ch1
    print(f"Propagation delay: {propagation_delay * 1e9:.2f} ns")
else:
    print("Could not find crossing time on one or both channels.")



### -- oscilloscope plot -- ###


# Plot
plt.figure(figsize=(10, 5))
plt.plot(time1, volts1, label='CH1', color='blue')
plt.plot(time2, volts2, label='CH2', color='red')
plt.title("Waveforms from CH1 and CH2")
plt.xlabel("Time (nS)")
plt.ylabel("Voltage (V)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()