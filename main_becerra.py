from dev_setup import find_instruments

osc, dmm, psu, fg = find_instruments()


osc.write("SELECT:CH1 ON")
osc.write("SELECT:CH2 ON")
print("Oscilloscope ready.")
