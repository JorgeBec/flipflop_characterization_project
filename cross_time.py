import pandas as pd
import numpy as np

# Load the CSV files
df1 = pd.read_csv("ch1.csv")  # Contains Time (s), Voltage (V)
df2 = pd.read_csv("ch2.csv")

time1 = df1["Time (s)"].to_numpy()
volts1 = df1["Voltage (V)"].to_numpy()

time2 = df2["Time (s)"].to_numpy()
volts2 = df2["Voltage (V)"].to_numpy()

def find_simple_crossing_time(time, voltage):
    threshold = (np.max(voltage) + np.min(voltage)) / 2
    for i in range(len(voltage)):
        if voltage[i] >= threshold:
            return time[i]
    return None

