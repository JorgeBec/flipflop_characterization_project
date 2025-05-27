import pyvisa
import numpy as np
import matplotlib as plt
import re

rm = pyvisa.ResourceManager()

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


def capture_and_plot_oscilloscope_data():
    rm = pyvisa.ResourceManager()
    devices = rm.list_resources()
    print("Connected VISA devices", devices)

    # Open your oscilloscope resource (adjust index if needed)
    osc = rm.open_resource(devices[0])
    print(osc.query("*IDN?"))

    # Stop acquisition before reading data
    osc.write("STOP")

    # Set data source to channel 1
    osc.write("WAVEFORMSOURCE CHAN1")

    # Set data encoding and width
    osc.write("WAVEFORMFORMAT BYTE")  # 8-bit data
    osc.write("WAVEFORMPOINTS 1000") # number of data points

    # Query preamble to get scaling info
    preamble = osc.query("WAVEFORMPREAMBLE?").strip().split(',')
    # Preamble format varies, for Tektronix TDS1000 series
    # [format, type, points, count, xIncrement, xOrigin, xReference, yIncrement, yOrigin, yReference]

    x_increment = float(preamble[4])  # time between points (sec)
    x_origin = float(preamble[5])     # start time (sec)
    y_increment = float(preamble[7])  # volts per bit
    y_origin = float(preamble[8])     # vertical offset (volts)
    y_reference = float(preamble[9])  # ADC value at zero volts

    # Request waveform data
    raw_data = osc.query_binary_values("WAVEFORMDATA?", datatype='B', container=np.array)

    # Convert raw data to volts
    volts = (raw_data - y_reference) * y_increment + y_origin

    # Create time axis
    times = x_origin + np.arange(len(raw_data)) * x_increment

    # Plot
    plt.figure(figsize=(10, 5))
    plt.plot(times * 1e3, volts)  # time in ms
    plt.title("Oscilloscope Channel 1 Capture")
    plt.xlabel("Time (ms)")
    plt.ylabel("Voltage (V)")
    plt.grid(True)
    plt.show()

    # Restart oscilloscope acquisition if needed
    osc.write("RUN")

if __name__ == "__main__":
    capture_and_plot_oscilloscope_data()
