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

# ------------------- Configure GW Instek AFG-2005 -------------------

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
                gen.write("SOUR1:APPLy:SQU 1000,5,2.5")  # 1kHz, 5Vpp, 2.5V offset
                time.sleep(0.2)
                gen.write("OUTP1 ON")

                freq = gen.query("SOUR1:FREQ?")
                volt = gen.query("SOUR1:VOLT?")
                offs = gen.query("SOUR1:VOLT:OFFS?")
                outp = gen.query("OUTP1?")

                print("Generador de funciones configurado:")
                print(f" - Frecuencia: {freq.strip()} Hz")
                print(f" - Amplitud: {volt.strip()} Vpp")
                print(f" - Offset: {offs.strip()} V")
                print(f" - Salida: {'ON' if outp.strip() == '1' else 'OFF'}")

                return gen
        except Exception:
            pass
    return None

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
        time.sleep(0.5)

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

# ------------------- Descending Voltage Sweep Routine -------------------

def perform_descending_voltage_sweep(ao_channel='Dev1/ao0', fluke_port='ASRL9::INSTR'):
    results = []

    for voltage in [round(v * 0.1, 2) for v in range(50, -1, -1)]:
        print(f"\nApplying {voltage} V to {ao_channel}...")
        set_daq_analog_output(ao_channel, voltage)
        time.sleep(0.5)  # Ensure a clock edge passes

        measured = read_voltage_with_fluke45(port=fluke_port)
        results.append({'AO Voltage (V)': voltage, 'Measured Voltage (V)': measured})

    df = pd.DataFrame(results)
    print("\nDescending Sweep Results:")
    print(df.to_string(index=False))

    df.to_csv("voltage_sweep_descending_results.csv", index=False)
    print("\nResults saved to 'voltage_sweep_descending_results.csv'.")

    return df

# ------------------- Main -------------------

if __name__ == "__main__":
    # Detect and configure GW Instek AFG-2005
    function_generator = detect_and_configure_gwinstek_afg()
    if not function_generator:
        print("Generador de funciones GW Instek AFG-2005 no detectado.")

    # Detect and configure Siglent power supply
    power_supply = detect_siglent_power_supply()
    if power_supply:
        configure_power_supply_ch1_5v(power_supply)
    else:
        print("Fuente Siglent SPD3303X-E no detectada.")

    # Perform voltage sweep
    perform_descending_voltage_sweep(ao_channel='Dev1/ao0', fluke_port='ASRL9::INSTR')
