import pyvisa
import nidaqmx
import numpy as np
import time

import pandas as pd

import matplotlib.pyplot as plt
from ff_setup import initialize_daq_outputs_zero
from cap_ch import capture_channel
#from td_crossing_time import find_crossing_time

rm = pyvisa.ResourceManager()
devices = rm.list_resources()

osc = rm.open_resource(devices[0])

initialize_daq_outputs_zero("Dev1")
### -- User inputs -- ###

#vcc_user = float(input("Vcc = "))
#freq_user = float(input("f = "))
type_test = input("1) HL\n2) LH \nIngresa el tipo de prueba \n")


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
### -- display set -- ###



### -- DAQ set --###
if type_test == "1":
    initialize_daq_outputs_zero("Dev1")
    with nidaqmx.Task() as task:    
        task.ao_channels.add_ao_voltage_chan("Dev1/ao0", min_val=0, max_val=5) #K
        task.ao_channels.add_ao_voltage_chan("Dev1/ao1", min_val=0, max_val=5) #J
        task.write([0, 5])  # Write voltages to ao0 and ao1 simultaneously
    
    ##negative flank
    with nidaqmx.Task() as task:
        task.do_channels.add_do_chan("Dev1/port1/line3")
        task.write(True)  # Write voltages to ao0 and ao1 simultaneously
        time.sleep(0.1)  # Wait for 100 ms
        task.write(False)  # Write voltages to ao0 and ao1 simultaneously
    
    with nidaqmx.Task() as task:       
        task.ao_channels.add_ao_voltage_chan("Dev1/ao0", min_val=0, max_val=5) #K
        task.ao_channels.add_ao_voltage_chan("Dev1/ao1", min_val=0, max_val=5) #J
        task.write([5, 0])  # Write voltages to ao0 and ao1 simultaneously      

elif type_test == "2":
    initialize_daq_outputs_zero("Dev1")
    with nidaqmx.Task() as task:    
        task.ao_channels.add_ao_voltage_chan("Dev1/ao0", min_val=0, max_val=5) #K
        task.ao_channels.add_ao_voltage_chan("Dev1/ao1", min_val=0, max_val=5) #J
        task.write([5, 0])  # Write voltages to ao0 and ao1 simultaneously


    ##negative flank
    with nidaqmx.Task() as task:
        task.do_channels.add_do_chan("Dev1/port1/line3")
        task.write(True)  # Write voltages to ao0 and ao1 simultaneously
        time.sleep(0.1)  # Wait for 100 ms
        task.write(False)  # Write voltages to ao0 and ao1 simultaneously

        
    with nidaqmx.Task() as task:        
        task.ao_channels.add_ao_voltage_chan("Dev1/ao0", min_val=0, max_val=5) #K
        task.ao_channels.add_ao_voltage_chan("Dev1/ao1", min_val=0, max_val=5) #J
        task.write([0, 5])  # Write voltages to ao0 and ao1 simultaneously

### capture with negative flank
with nidaqmx.Task() as task:
    task.do_channels.add_do_chan("Dev1/port1/line3")
    task.write(True)  # Write voltages to ao0 and ao1 simultaneously
    time.sleep(0.1)  # Wait for 100 ms
    task.write(False)  # Write voltages to ao0 and ao1 simultaneously

time.sleep(0.1)  # Wait for 100 ms
### -- DAQ set --###

############ Capture both channels ############
time1, volts1 = capture_channel(1)
time2, volts2 = capture_channel(2)
############ Capture both channels ############


##########  Save data to CSV files  ########
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
##########  Save data to CSV files  ########



initialize_daq_outputs_zero("Dev1")
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