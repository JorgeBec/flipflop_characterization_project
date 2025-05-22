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

# ------------------- Detect and Configure Siglent Power Supply -------------------

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

def configure_power_supply_ch1_0v_off(supply):
    try:
        supply.write("CH1:VOLT 0")
        supply.write("OUTP CH1,OFF")
        print("Power supply CH1 set to 0 V and turned OFF.")
    except Exception as e:
        print("Error setting power supply CH1 to 0 V and OFF:", e)

def configure_power_supply_ch1_5v_on(supply):
    try:
        supply.write("CH1:VOLT 5")
        supply.write("CH1:CURR 0.1")
        supply.write("OUTP CH1,ON")
        print("Power supply CH1 configured to 5 V and turned ON.")
    except Exception as e:
        print("Error configuring power supply CH1:", e)

def power_supply_ch1_off(supply):
    try:
        supply.write("OUTP CH1,OFF")
        print("Power supply CH1 turned OFF.")
    except Exception as e:
        print("Error turning off power supply CH1:", e)

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
                gen.write("SOUR1:APPLy:SQU 1000,5,2.5")
                time.sleep(0.2)
                gen.write("OUTP1 ON")

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

# ------------------- Set Digital Output (for CLR and PRE) -------------------

def set_digital_output(line, value):
    with nidaqmx.Task() as task:
        task.do_channels.add_do_chan(line)
        task.write(value)
        print(f"Digital line {line} set to {'HIGH' if value else 'LOW'}.")

# ------------------- Read Voltage from Fluke 45 Multimeter -------------------

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

# ------------------- Voltage Sweep Routine -------------------

def perform_voltage_sweep_and_measure(ao_j='Dev1/ao0', ao_k='Dev1/ao1', fluke_port='ASRL9::INSTR'):
    results = []
    logic_threshold = 2.5

    set_digital_output('Dev1/port1/line1', False)
    print("Digital line Dev1/port1/line1 set to LOW (initial condition).")

    for voltage in [round(v * 0.1, 2) for v in range(0, 26)]:
        print(f"\nApplying {voltage} V to J (AO0)...")
        set_daq_analog_output(ao_j, voltage)
        set_daq_analog_output(ao_k, 0.0)
        time.sleep(0.5)

        measured = read_voltage_with_fluke45(port=fluke_port)

        try:
            measured_val = float(measured)
            logic_state = "H" if measured_val >= logic_threshold else "L"
        except:
            logic_state = "?"

        results.append({
            'J Voltage (V)': voltage,
            'Measured Voltage (V)': measured,
            'Q State': logic_state
        })

    df = pd.DataFrame(results)
    print("\nSweep Results:")
    print(df.to_string(index=False))

    df.to_csv("voltage_sweep_results.csv", index=False)
    print("\nResults saved to 'voltage_sweep_results.csv'.")

    return df

# ------------------- Main -------------------

if __name__ == "__main__":
    power_supply = detect_siglent_power_supply()
    if power_supply:
        configure_power_supply_ch1_0v_off(power_supply)
        time.sleep(3)
        configure_power_supply_ch1_5v_on(power_supply)
        afg = detect_and_configure_gwinstek_afg()
        if not afg:
            print("GW Instek AFG-2005 generator not detected.")
    else:
        print("Siglent SPD3303X-E power supply not detected.")

    set_digital_output('Dev1/port1/line0', False)
    time.sleep(1)
    set_digital_output('Dev1/port1/line0', True)

    set_daq_analog_output('Dev1/ao0', 0.0)
    set_daq_analog_output('Dev1/ao1', 1.0)

    perform_voltage_sweep_and_measure(ao_j='Dev1/ao0', ao_k='Dev1/ao1', fluke_port='ASRL9::INSTR')

    set_daq_analog_output('Dev1/ao0', 0.0)
    set_daq_analog_output('Dev1/ao1', 0.0)

    set_digital_output('Dev1/port1/line0', False)

    if power_supply:
        power_supply_ch1_off(power_supply)