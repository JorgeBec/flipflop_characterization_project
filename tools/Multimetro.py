import pyvisa
import time
import re

def remove_duplicate(measurement):
    """
    Detects and removes duplicate measurement values in the string.
    Example: "+22.009E+3+22.009E+3" -> "+22.009E+3"
    """
    measurement = measurement.strip()
    
    # Use a regular expression to match values like +22.009E+3
    pattern = r'[+-]?\d+\.\d+E[+-]?\d+'
    matches = re.findall(pattern, measurement)

    # If at least one value is found, return the first one
    if matches:
        return matches[0]

    # If no pattern is found, return the original string
    return measurement

try:
    rm = pyvisa.ResourceManager()
    # List connected devices to verify
    devices = rm.list_resources()
    print("Connected devices:", devices)
    
    # Open the multimeter resource (adjust if your port is different)
    instrument = rm.open_resource('ASRL5::INSTR')
    
    # Configure communication parameters:
    instrument.baud_rate = 9600  # Make sure this matches your multimeter
    instrument.timeout = 5000    # Increased timeout to 5000 ms
    
    # Switch to voltage measurement function
    instrument.write("VOLT")
    print("Multimeter set to voltage function (Volts).")
    
    # Wait a few seconds for the function switch to stabilize
    time.sleep(2)
    
    # Get the measurement using VAL1?
    try:
        measured_value = instrument.query("VAL1?")
        measured_value = measured_value.strip()
        # print("Measured value (VAL1?):", measured_value)
    except Exception as e:
        print("Error getting measured value with VAL1?:", e)
    
    # Get the measurement using MEAS1?
    try:
        measured_value_meas = instrument.query("MEAS1?")
        measured_value_meas = measured_value_meas.strip()
        # print("Raw response (MEAS1?):", measured_value_meas)
        
        # Process the response to remove duplication
        corrected_value = remove_duplicate(measured_value_meas)
        print("Voltage Value:", corrected_value)
    except Exception as e:
        print("Error getting measured value with MEAS1?:", e)

except Exception as e:
    print("Error connecting or communicating with the multimeter:", e)
