import numpy as np

import pandas as pd

import matplotlib.pyplot as plt
from ff_setup import initialize_daq_outputs_zero
from cap_ch import capture_channel

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