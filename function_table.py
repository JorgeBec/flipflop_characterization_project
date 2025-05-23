import pyvisa
import nidaqmx
import time
import re
import csv

# ------------------- Fluke 45 Multimeter -------------------
def remove_duplicate(measurement):
    pattern = r'[+-]?\d+\.\d+E[+-]?\d+'
    matches = re.findall(pattern, measurement.strip())
    return matches[0] if matches else measurement

def read_voltage_fluke45(port='ASRL9::INSTR'):
    try:
        rm = pyvisa.ResourceManager()
        multimeter = rm.open_resource(port)
        multimeter.baud_rate = 9600
        multimeter.timeout = 5000
        multimeter.write("VOLT")
        time.sleep(2)

        try:
            multimeter.query("VAL1?")
        except:
            pass  # Ignored, just to stabilize the reading

        try:
            meas = multimeter.query("MEAS1?")
            return float(remove_duplicate(meas))
        except Exception as e:
            print("Error in MEAS1?:", e)
            return None
    except Exception as e:
        print("Error communicating with Fluke 45:", e)
        return None

# ------------------- DAQ -------------------
def set_daq_analog_output(channel, voltage):
    with nidaqmx.Task() as task:
        # Make sure the range is valid for your DAQ (e.g., NI USB-6008 = 0-5 V)
        task.ao_channels.add_ao_voltage_chan(
            physical_channel=channel,
            min_val=0.0,
            max_val=5.0
        )
        task.write(voltage)

def set_daq_digital_output(channel, state):
    with nidaqmx.Task() as task:
        task.do_channels.add_do_chan(channel)
        task.write(bool(state))

def pulse_clk(channel='Dev1/port1/line1', duration=0.05):
    set_daq_digital_output(channel, True)
    time.sleep(duration)
    set_daq_digital_output(channel, False)
    time.sleep(duration)

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

def power_supply_ch1_off(supply):
    try:
        supply.write("OUTP CH1,OFF")
        #print("Power supply CH1 turned OFF.")
    except Exception as e:
        print("Error turning off power supply CH1:", e)

# ------------------- Signal Generator -------------------
def detect_afg_2005():
    rm = pyvisa.ResourceManager()
    for res in rm.list_resources():
        try:
            gen = rm.open_resource(res)
            gen.baud_rate = 9600
            gen.data_bits = 8
            gen.parity = pyvisa.constants.Parity.none
            gen.stop_bits = pyvisa.constants.StopBits.one
            gen.write_termination = '\r\n'
            gen.read_termination = '\r\n'
            gen.timeout = 3000
            if "GW INSTEK" in gen.query("*IDN?") and "AFG-2005" in gen.query("*IDN?"):
                return gen
        except:
            pass
    return None

# ------------------- Function Table -------------------
def generate_function_table():
    #print("Initializing...")

    # Turn off generator
    gen = detect_afg_2005()
    if gen:
        gen.write("OUTP1 OFF")
        #print("AFG-2005 generator turned off.")

    # Power supply
    psu = detect_siglent_power_supply()
    if psu:
        psu.write("CH1:VOLT 0")
        psu.write("OUTP CH1,OFF")
        #print("CH1 turned off and set to 0 V.")
        time.sleep(3)
        psu.write("CH1:VOLT 5")
        psu.write("CH1:CURR 0.1")
        psu.write("OUTP CH1,ON")
        #print("CH1 turned on at 5 V.")
    else:
        print("SIGLENT power supply not detected.")
        return

    time.sleep(1)
    print("\nGenerating function table...\n")
    print(" CLR  |   J   |   K   |   Q (V)")
    print("----------------------------------")

    tests = [
        (0, 'X', 'X'),         # CLR = 0 → reset
        (1, 0.0, 0.0),         # JK = 00 → hold
        (1, 5.0, 0.0),         # JK = 01 → reset
        (1, 0.0, 5.0),         # JK = 10 → set
        (1, 5.0, 5.0),         # JK = 11 → toggle
    ]

    results = []

    for clr, j, k in tests:
        set_daq_digital_output("Dev1/port1/line0", clr)

        if j == 'X':
            set_daq_analog_output("Dev1/ao0", 0.0)
            set_daq_analog_output("Dev1/ao1", 0.0)
        else:
            set_daq_analog_output("Dev1/ao0", j)
            set_daq_analog_output("Dev1/ao1", k)

        time.sleep(0.2)
        pulse_clk()

        time.sleep(0.5)
        voltage = read_voltage_fluke45() or "?>"
        print(f"  {clr}   |  {j}  |  {k}  |   {voltage}")
        results.append((clr, j, k, voltage))

    # Save CSV
    with open("function_table.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["CLR", "J", "K", "Q (V)"])
        for row in results:
            writer.writerow(row)

    print("\nTable saved to 'function_table.csv'.")

# ------------------- MAIN -------------------
# ------------------- MAIN -------------------
if __name__ == "__main__":
    psu = None
    try:
        generate_function_table()
    finally:
        # Shutdown power supply at the end
        if psu is None:
            psu = detect_siglent_power_supply()
        if psu:
            try:
                psu.write("CH1:VOLT 0")
                psu.write("OUTP CH1,OFF")
                print("Finalization: CH1 set to 0 V and turned OFF.")
            except Exception as e:
                #print("Error during final power supply shutdown:", e)
                pass
        else:
            print("No power supply detected at program end.")

    
