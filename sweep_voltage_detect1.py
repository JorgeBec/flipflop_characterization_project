import pyvisa
import time
import re
import nidaqmx
from tabulate import tabulate

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
    siglent_pattern = re.compile(r"SIGLENT.*SPD3303X-E", re.IGNORECASE)

    for resource in resources:
        try:
            instrument = rm.open_resource(resource)
            instrument.timeout = 3000
            idn = instrument.query("*IDN?").strip()
            if siglent_pattern.search(idn):
                return instrument
        except Exception:
            pass
    return None

def configure_power_supply_ch1_0v_off(supply):
    try:
        supply.write("CH1:VOLT 0")
        supply.write("OUTP CH1,OFF")
        #print("Power supply CH1 set to 0 V and turned OFF.")
    except Exception as e:
        print("Error setting power supply CH1 to 0 V and OFF:", e)

def configure_power_supply_ch1_5v_on(supply):
    try:
        supply.write("CH1:VOLT 5")
        supply.write("CH1:CURR 0.1")
        supply.write("OUTP CH1,ON")
        #print("Power supply CH1 configured to 5 V and turned ON.")
    except Exception as e:
        print("Error configuring power supply CH1:", e)

def power_supply_ch1_off(supply):
    try:
        supply.write("OUTP CH1,OFF")
        #print("Power supply CH1 turned OFF.")
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

# ------------------- Set Digital Output (for CLR and PRE) -------------------

def set_digital_output(line, value):
    with nidaqmx.Task() as task:
        task.do_channels.add_do_chan(line)
        task.write(value)
        #print(f"Digital line {line} set to {'HIGH' if value else 'LOW'}.")

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
        time.sleep(1)

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

# ------------------- Validate Voltage Reading -------------------

def is_valid_voltage(val_str, min_v=0.0, max_v=6.0):
    try:
        val = float(val_str)
        return min_v <= val <= max_v
    except (ValueError, TypeError):
        return False

def read_voltage_with_validation(port='ASRL9::INSTR', max_retries=5, delay=1):
    for attempt in range(max_retries):
        voltage_str = read_voltage_with_fluke45(port)
        if is_valid_voltage(voltage_str):
            return voltage_str
        print(f"Invalid reading '{voltage_str}', retrying ({attempt + 1}/{max_retries})...")
        time.sleep(delay)
    print("Warning: Maximum retries reached. Returning last invalid reading.")
    return voltage_str

# ------------------- Voltage Sweep Routine (with tabulate) -------------------

def perform_voltage_sweep_and_measure(ao_j='Dev1/ao0', ao_k='Dev1/ao1', fluke_port='ASRL9::INSTR'):
    results = []
    logic_threshold = 2.5

    set_digital_output('Dev1/port1/line1', False)
    #print("Digital line Dev1/port1/line1 set to LOW (initial condition).")

    for voltage in [round(v * 0.05, 2) for v in range(0, 31)]:
        print(f"\nApplying {voltage} V to J (AO0)...")
        set_daq_analog_output(ao_j, voltage)
        set_daq_analog_output(ao_k, 0.0)
        time.sleep(1)

        measured = read_voltage_with_validation(port=fluke_port)

        try:
            measured_val = float(measured)
            logic_state = "H" if measured_val >= logic_threshold else "L"
        except:
            logic_state = "?"

        results.append([
            voltage,
            measured,
            logic_state
        ])

    headers = ["J Voltage (V)", "Q Voltage (V)", "Q Logic State"]
    print("\nSweep Results:")
    print(tabulate(results, headers=headers, tablefmt="grid"))

    with open("voltage_ascending_sweep_results.csv", "w") as f:
        f.write(",".join(headers) + "\n")
        for row in results:
            f.write(",".join(str(x) for x in row) + "\n")

    print("\nResults saved to 'voltage_ascending_sweep_results.csv'.")
    return results

# ------------------- Main -------------------

if __name__ == "__main__":
    power_supply = detect_siglent_power_supply()
    if power_supply:
        configure_power_supply_ch1_0v_off(power_supply)
        time.sleep(3)
        configure_power_supply_ch1_5v_on(power_supply)
    else:
        print("Siglent SPD3303X-E power supply not detected.")
    
    detect_and_configure_gwinstek_afg()
    time.sleep(1)
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
