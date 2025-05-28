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

# ------------------- Generate Clock Pulse Using DAQ -------------------

def send_daq_clock_pulse(clk_line, high_time=0.01):
    with nidaqmx.Task() as task:
        task.do_channels.add_do_chan(clk_line)
        task.write(False)
        time.sleep(0.01)
        task.write(True)
        time.sleep(high_time)
        task.write(False)
        print("Clock pulse sent using DAQ.")

# ------------------- Set Digital Output (for CLR or similar control) -------------------

def set_digital_output(line, value):
    with nidaqmx.Task() as task:
        task.do_channels.add_do_chan(line)
        task.write(value)
        #print(f"Digital line {line} set to {'HIGH' if value else 'LOW'}.")

# ------------------- Control AFG Output -------------------

def control_afg_output(turn_on=True):
    try:
        rm = pyvisa.ResourceManager()
        for resource in rm.list_resources():
            try:
                inst = rm.open_resource(resource)
                inst.baud_rate = 9600
                inst.data_bits = 8
                inst.parity = pyvisa.constants.Parity.none
                inst.stop_bits = pyvisa.constants.StopBits.one
                inst.write_termination = '\r\n'
                inst.read_termination = '\r\n'
                inst.timeout = 3000

                idn = inst.query("*IDN?")
                if "GW INSTEK" in idn.upper() and "AFG-2005" in idn.upper():
                    inst.write(f"OUTP1 {'ON' if turn_on else 'OFF'}")
                    #print(f"AFG-2005 output {'enabled' if turn_on else 'disabled'}.")
                    return
            except Exception:
                continue
    except Exception as e:
        print("Error controlling AFG output:", e)

# ------------------- Control SPD3303X-E Power Supply -------------------

def control_siglent_ch1(voltage=0.0, current=0.1, output_on=True):
    try:
        rm = pyvisa.ResourceManager()
        for resource in rm.list_resources():
            try:
                inst = rm.open_resource(resource)
                inst.baud_rate = 9600
                inst.timeout = 3000
                inst.write_termination = '\n'
                inst.read_termination = '\n'

                idn = inst.query("*IDN?")
                if "SIGLENT" in idn.upper() and "SPD3303X" in idn.upper():
                    inst.write(f"CH1:VOLT {voltage}")
                    inst.write(f"CH1:CURR {current}")
                    inst.write("CH1:MODE VOLT")
                    inst.write(f"OUTP CH1,{'ON' if output_on else 'OFF'}")
                    #print(f"SIGLENT CH1 set to {voltage} V, {current} A, Output {'ON' if output_on else 'OFF'}.")
                    return
            except Exception:
                continue
    except Exception as e:
        print("Error controlling SPD3303X-E:", e)


# ------------------- Power Supply -------------------
def detect_siglent_power_supply():
    rm = pyvisa.ResourceManager()
    for resource in rm.list_resources():
        try:
            instrument = rm.open_resource(resource)
            idn = instrument.query("*IDN?").strip()
            #print(f"Detected: {resource} → {idn}")
            if "SIGLENT" in idn.upper() and "SPD3303X-E" in idn.upper():
                return instrument
        except Exception as e:
            print(f"Error with {resource}: {e}")
            continue
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
        
def configure_power_supply_ch2_0v_off(supply):
    try:
        supply.write("CH2:VOLT 0")
        supply.write("OUTP CH2,OFF")
        #print("Power supply CH2 set to 0 V and turned OFF.")
    except Exception as e:
        print("Error setting power supply CH2 to 0 V and OFF:", e)

def configure_power_supply_ch2_5v_on (supply):
    try:
        supply.write("CH2:VOLT 5")
        supply.write("CH2:CURR 0.1")
        supply.write("OUTP CH2,ON")
        #print("Power supply CH2 configured to 5 V and turned ON.")
    except Exception as e:
        print("Error configuring power supply CH2:", e)

# ------------------- Read Voltage from Fluke 45 Multimeter -------------------

def remove_duplicate(measurement):
    measurement = measurement.strip()
    pattern = r'[+-]?\d+\.\d+E[+-]?\d+'
    matches = re.findall(pattern, measurement)
    return matches[0] if matches else measurement

def read_voltage_with_fluke45(port='ASRL10::INSTR'):
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

# ------------------- Voltage Sweep Routine (Descending) -------------------

def perform_descending_voltage_sweep_and_measure(ao_j='Dev2/ao0', ao_k='Dev2/ao1',
                                                  fluke_port='ASRL10::INSTR',
                                                  clk_line='Dev2/port1/line1',
                                                  clr_line='Dev2/port1/line0'):
    results = []

    set_digital_output(clr_line, False)
    time.sleep(0.5)
    set_digital_output(clr_line, True)
    time.sleep(0.5)

    #print("\nInitializing Q to logic 1 (J=1, K=0, clock pulse)...")
    set_daq_analog_output(ao_j, 5.0)
    set_daq_analog_output(ao_k, 0.0)
    send_daq_clock_pulse(clk_line)
    time.sleep(1)

    for voltage in [round(v * 0.05, 2) for v in reversed(range(0, 31))]:
        print(f"\nApplying {voltage} V to J (AO0)...")
        set_daq_analog_output(ao_j, voltage)
        set_daq_analog_output(ao_k, 5.0)
        send_daq_clock_pulse(clk_line)
        time.sleep(1)

        measured = read_voltage_with_validation(port=fluke_port)

        try:
            logic_q = 'H' if float(measured) > 2.0 else 'L'
        except:
            logic_q = '?'

        results.append([voltage, measured, logic_q])

    headers = ["J Voltage (V)", "Q Voltage (V)", "Q Logic State"]
    print("\nSweep Results:")
    print(tabulate(results, headers=headers, tablefmt="grid"))

    with open("voltage_descending_sweep_results.csv", "w") as f:
        f.write(",".join(headers) + "\n")
        for row in results:
            f.write(",".join(str(x) for x in row) + "\n")

    print("\nResults saved to 'voltage_descending_sweep_results.csv'.")
    return results

# ------------------- Validate Voltage Reading -------------------

def is_valid_voltage(val_str, min_v=0.0, max_v=6.0):
    try:
        val = float(val_str)
        return min_v <= val <= max_v
    except (ValueError, TypeError):
        return False

def read_voltage_with_validation(port='ASRL10::INSTR', max_retries=5, delay=1):
    for attempt in range(max_retries):
        voltage_str = read_voltage_with_fluke45(port)
        if is_valid_voltage(voltage_str):
            return voltage_str
        #print(f"Invalid reading '{voltage_str}', retrying ({attempt + 1}/{max_retries})...")
        time.sleep(delay)
    print("Warning: Maximum retries reached. Returning last invalid reading.")
    return voltage_str

# ------------------- Main -------------------

if __name__ == "__main__":

    power_supply = detect_siglent_power_supply()
    if power_supply:
        configure_power_supply_ch1_0v_off(power_supply)
        configure_power_supply_ch2_0v_off(power_supply)
        time.sleep(3)
        configure_power_supply_ch1_5v_on(power_supply)
        configure_power_supply_ch2_5v_on(power_supply)
    else:
        print("Siglent SPD3303X-E power supply not detected.")

    control_afg_output(False)
    control_siglent_ch1(voltage=0.0, current=0.1, output_on=False)
    time.sleep(3)
    control_siglent_ch1(voltage=5.0, current=0.1, output_on=True)
    set_digital_output('Dev2/port1/line1', False)

    perform_descending_voltage_sweep_and_measure(
        ao_j='Dev2/ao0',
        ao_k='Dev2/ao1',
        fluke_port='ASRL9::INSTR',
        clk_line='Dev2/port1/line1',
        clr_line='Dev2/port1/line0'
    )

    set_daq_analog_output('Dev2/ao0', 0.0)
    set_daq_analog_output('Dev2/ao1', 0.0)
    set_digital_output('Dev2/port1/line0', False)
    control_siglent_ch1(voltage=0.0, current=0.1, output_on=False)
