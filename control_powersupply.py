import pyvisa

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

def configure_channel(supply, channel):
    while True:
        try:
            voltage = float(input(f"Enter voltage for {channel} (0 - 7 V): "))
            if 0 <= voltage <= 7:
                supply.write(f"{channel}:VOLT {voltage}")
                supply.write(f"{channel}:CURR 0.1")  # Limit current to 100 mA
                supply.write(f"OUTP {channel},ON")
                print(f"{channel} set to {voltage} V, 100 mA current limit, and turned on.")
                break
            else:
                print("Voltage must be between 0 and 7 V.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def initialize_power_supply(supply):
    # Set both channels to 0V and 100mA at startup
    for ch in ["CH1", "CH2"]:
        supply.write(f"{ch}:VOLT 0")
        supply.write(f"{ch}:CURR 0.1")
        supply.write(f"OUTP {ch},ON")
    print("Both channels initialized to 0V, 100 mA current limit, and turned on.")

# --- Main program ---

power_supply = detect_siglent_power_supply()
if power_supply:
    initialize_power_supply(power_supply)
    configure_channel(power_supply, "CH1")
    configure_channel(power_supply, "CH2")
