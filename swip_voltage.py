import pyvisa
import time
import re
import nidaqmx
import pandas as pd

# ------------------- Configure Analog Output (DAQ) -------------------

def set_daq_analog_output(channel, voltage):
    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan(
            physical_channel=channel,
            min_val=0.0,
            max_val=5.0
        )
        task.write(voltage)

# ------------------- Configure Siglent Power Supply -------------------

def detect_siglent_power_supply():
    rm = pyvisa.ResourceManager()
    resources = rm.list_resources()
    for resource in resources:
        try:
            instrument = rm.open_resource(resource)
            idn = instrument.query("*IDN?")
            if "SIGLENT" in idn.upper() and "SPD3303X-E" in idn.upper():
                return instrument
        except Exception:
            pass
    return None

def configure_power_supply_ch1_5v(supply):
    try:
        supply.write("CH1:VOLT 5")
        supply.write("CH1:CURR 0.1")
        supply.write("OUTP CH1,ON")
        print("Power supply CH1 configured to 5 V and turned ON.")
    except Exception as e:
        print("Error configuring power supply:", e)

# ------------------- Read Voltage from Fluke 45 -------------------

def remove_duplicate(measurement):
    measurement = measurement.strip()
    pattern = r'[+-]?\d+\.\d+E[+-]?\d+'
    matches = re.findall(pattern, measurement)
    return matches[0] if matches else measurement

def read_voltage_with_fluke45(port='ASRL9::INSTR'):
    try:
        rm = pyvisa.ResourceManager()
        instrument = rm.open_resource(port)
        instrument.baud_rate = 9600
        instrument.timeout = 5000

        instrument.write("VOLT")
        time.sleep(2)

        try:
            instrument.query("VAL1?")
        except Exception:
            pass

        try:
            meas1 = instrument.query("MEAS1?").strip()
            voltage = remove_duplicate(meas1)
            print(f"Measured voltage: {voltage} V")
            return voltage
        except Exception as e:
            print("Error reading MEAS1?:", e)
            return None

    except Exception as e:
        print("Error connecting to multimeter:", e)
        return None

# ------------------- Voltage Sweep Routine -------------------

def perform_voltage_sweep_and_measure(ao_channel='Dev1/ao0', fluke_port='ASRL9::INSTR'):
    results = []

    for voltage in [round(v * 0.1, 2) for v in range(0, 51)]:
        print(f"\nApplying {voltage} V to {ao_channel}...")
        set_daq_analog_output(ao_channel, voltage)
        time.sleep(1)  # Allow time for settling

        measured = read_voltage_with_fluke45(port=fluke_port)
        results.append({'AO Voltage (V)': voltage, 'Measured Voltage (V)': measured})

    df = pd.DataFrame(results)
    print("\nSweep Results:")
    print(df.to_string(index=False))

    df.to_csv("voltage_sweep_results.csv", index=False)
    print("\nResults saved to 'voltage_sweep_results.csv'.")

    return df

# ------------------- Main -------------------

if __name__ == "__main__":
    # Configure CH1 to 5 V if power supply is connected
    power_supply = detect_siglent_power_supply()
    if power_supply:
        configure_power_supply_ch1_5v(power_supply)
    else:
        print("Siglent SPD3303X-E power supply not detected.")

    # Perform the voltage sweep and measurements
    perform_voltage_sweep_and_measure(ao_channel='Dev1/ao0', fluke_port='ASRL9::INSTR')
