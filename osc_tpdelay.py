import pyvisa
from osc_setup import setup_oscilloscope 
from dev_setup import find_instruments

osc, dmm, psu, fg = find_instruments()

if osc:
    print(osc.query("*IDN?"))
    setup_oscilloscope(osc)  # only call setup if osc is valid
else:
    print("Oscilloscope not found.")

