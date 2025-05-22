import nidaqmx

def initialize_daq_outputs_zero(device_name="Dev1"):
    with nidaqmx.Task() as task:
        # Add AO channels ao0 and ao1
        task.ao_channels.add_ao_voltage_chan(f"{device_name}/ao0", min_val=0, max_val=5)
        task.ao_channels.add_ao_voltage_chan(f"{device_name}/ao1", min_val=0, max_val=5)
        
        # Write 0 volts to both channels
        task.write([0.0, 0.0])
        print(f"Set {device_name}/ao0 and {device_name}/ao1 outputs to 0 V.")

if __name__ == "__main__":
    initialize_daq_outputs_zero()
