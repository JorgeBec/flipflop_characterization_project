import pyvisa
import time

def detect_siglent_power_supply():
    rm = pyvisa.ResourceManager()
    resources = rm.list_resources()

    for resource in resources:
        try:
            instrument = rm.open_resource(resource)
            idn = instrument.query("*IDN?")
            if "SIGLENT" in idn.upper() and "SPD3303X-E" in idn.upper():
                print(f"Power supply found: {idn.strip()} at {resource}")
                return instrument
        except Exception as e:
            print(f"Could not connect to {resource}: {e}")
    
    print("No SIGLENT SPD3303X-E power supply found.")
    return None

def initialize_power_supply(supply):
    # Set both channels to 0V and 100mA, and ensure outputs are OFF
    for ch in ["CH1", "CH2"]:
        supply.write(f"{ch}:VOLT 0")
        supply.write(f"{ch}:CURR 0.1")
        supply.write(f"OUTP {ch},OFF")
    print("Both channels initialized to 0V, 100 mA current limit, and outputs OFF.")

def configure_channel(supply, channel):
    while True:
        try:
            voltage = float(input(f"Enter voltage for {channel} (0 - 7 V): "))
            if 0 <= voltage <= 7:
                supply.write(f"{channel}:VOLT {voltage}")
                supply.write(f"{channel}:CURR 0.1")
                print(f"{channel} set to {voltage} V with 100 mA current limit.")
                break
            else:
                print("Voltage must be between 0 and 7 V.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def enable_outputs(supply):
    supply.write("OUTP CH1,ON")
    supply.write("OUTP CH2,ON")
    print("CH1 and CH2 outputs are now ON.")

def detect_and_configure_gwinstek_afg():
    import time
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
                print(f"Function generator found: {idn.strip()} at {resource}")

                gen.write("SOUR1:APPLy:SQU 1000,5,2.5")
                time.sleep(0.2)
                gen.write("OUTP1 ON")

                freq = gen.query("SOUR1:FREQ?")
                volt = gen.query("SOUR1:VOLT?")
                offs = gen.query("SOUR1:VOLT:OFFS?")
                outp = gen.query("OUTP1?")

                print("Square wave configured:")
                print(f" - Frequency: {freq.strip()} Hz")
                print(f" - Amplitude: {volt.strip()} Vpp")
                print(f" - Offset: {offs.strip()} V")
                print(f" - Output: {'ON' if outp.strip() == '1' else 'OFF'}")

                return gen
        except Exception as e:
            print(f"Could not connect to {resource}: {e}")
    
    print("No GW Instek AFG-2005 function generator found.")
    return None

# --- Main program ---
function_generator = detect_and_configure_gwinstek_afg()
if function_generator:
    print("Function generator configured successfully.")

power_supply = detect_siglent_power_supply()
if power_supply:
    initialize_power_supply(power_supply)
    configure_channel(power_supply, "CH1")
    configure_channel(power_supply, "CH2")
    enable_outputs(power_supply)
