# osc_setup.py
import pyvisa

def setup_oscilloscope():
    rm = pyvisa.ResourceManager()
    devices = rm.list_resources()
    osc = rm.open_resource(devices[0])

    print("Oscilloscope ID:", osc.query("*IDN?"))

    # Configuration commands
    osc.write("SELECT:CH1 ON")
    osc.write("SELECT:CH2 ON")
    osc.write("CH1:COUPLING DC")
    osc.write("CH2:COUPLING DC")
    osc.write("CH1:SCALE 1")
    osc.write("CH2:SCALE 1")
    osc.write("HORIZONTAL:MAIN:SCALE 1E-3")
    osc.write("TRIGGER:MAIN:MODE EDGE")
    osc.write("TRIGGER:MAIN:EDGE:SOURCE CH1")
    osc.write("TRIGGER:MAIN:EDGE:SLOPE RISE")
    osc.write("TRIGGER:MAIN:COUPLING DC")
    osc.write("TRIGGER:MAIN:LEVEL 2.5")

    print("Oscilloscope configured.")
    return osc  # Return the oscilloscope object if you want to keep using it
