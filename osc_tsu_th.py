import pyvisa
import nidaqmx
import numpy as np
import time

import pandas as pd

import matplotlib.pyplot as plt
from td_crossing_time import find_crossing_time
from ff_setup import initialize_daq_outputs_zero
from cap_ch import capture_channel

## -------------- func gen setup ----------------- ##

def detect_and_configure_gwinstek_afg():
    rm = pyvisa.ResourceManager()
    resources = rm.list_resources()

    for resource in resources:
        try:
            gen = rm.open_resource(resource)
            gen.baud_rate = 9600
            gen.data_bits = 8
            gen.parity = pyvisa.constants.Parity.none
            gen.stop_bits = pyvisa.constants.StopBits.one
            gen.write_termination = '\r\n'
            gen.read_termination = '\r\n'
            gen.timeout = 3000

            idn = gen.query("*IDN?")
            if "GW INSTEK" in idn.upper() and "AFG-2005" in idn.upper():
                gen.write("SOUR1:APPLy:SQU 1000,5,2.5")
                time.sleep(1)
                gen.write("OUTP1 ON")
                time.sleep(1)

                freq = gen.query("SOUR1:FREQ?")
                volt = gen.query("SOUR1:VOLT?")
                offs = gen.query("SOUR1:VOLT:OFFS?")
                outp = gen.query("OUTP1?")

                print("Function generator configured:")
                print(f" - Frequency: {freq.strip()} Hz")
                print(f" - Amplitude: {volt.strip()} Vpp")
                print(f" - Offset: {offs.strip()} V")
                print(f" - Output: {'ON' if outp.strip() == '1' else 'OFF'}")

                return gen
        except Exception:
            pass
    return None




## -------------- func gen seup ----------------- ##





def set_j(value):
    with nidaqmx.Task() as task:
        initialize_daq_outputs_zero("Dev1")
        task.ao_channels.add_ao_voltage_chan("Dev1/ao0", min_val=0, max_val=5) #J
        task.ao_channels.add_ao_voltage_chan("Dev1/ao1", min_val=0, max_val=5) #K
        task.write([value, 0])


def trigger_clk():

        ##  ----------negative ---------flank
    with nidaqmx.Task() as task:
        task.do_channels.add_do_chan("Dev1/port1/line1")
        task.write(True)  # Write voltages to ao0 and ao1 simultaneously
        time.sleep(0.1)  # Wait for 100 ms
        task.write(False)  # Write voltages to ao0 and ao1 simultaneously


def read_q():
    time2, volts2 = capture_channel(2)
    volt_out = (np.max(volts2))

    return volt_out

def test_setup_time(t_setup_ns):
    set_j(0)
    time.sleep(t_setup_ns * 1e-9)

    set_j(5)
    time.sleep(t_setup_ns * 1e-9)

    trigger_clk()
    time.sleep(1e-4)

    result = read_q()
    return result



detect_and_configure_gwinstek_afg()

## -------------- Oscilloscope setup ----------------- ##
rm = pyvisa.ResourceManager()
devices = rm.list_resources()

osc = rm.open_resource(devices[0])


## --------------- DAQ setup ----------------- ##
initialize_daq_outputs_zero("Dev1")




# Test loop
results = []
tested_times_ns = np.arange(20, 0, -10)


for t_ns in tested_times_ns:
    print(f"\nTesting setup time: {t_ns} ns")
    passed = test_setup_time(t_ns)
    results.append({"Tsu (ns)": t_ns, "Result": "PASS" if passed else "FAIL"})

# Convert to DataFrame
df = pd.DataFrame(results)

# Save to CSV
csv_filename = "tsu_results.csv"
df.to_csv(csv_filename, index=False)
print(f"\nResults saved to {csv_filename}")

# Optional: print summary
print("\nSummary:")
print(df)
