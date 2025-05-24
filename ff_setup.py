import nidaqmx
import time

def initialize_daq_outputs_zero(device_name="Dev1"):
    # Analog ports
    with nidaqmx.Task() as task:
        # J AO0 and K AO1
        task.ao_channels.add_ao_voltage_chan(f"{device_name}/ao0", min_val=0, max_val=5) #K
        task.ao_channels.add_ao_voltage_chan(f"{device_name}/ao1", min_val=0, max_val=5) #J

        task.write([0,0])

        
        
    #digital ports
    with nidaqmx.Task() as do_task:
        # CLR P1.0 and CLK P1.1
        do_task.do_channels.add_do_chan(f"{device_name}/port1/line2")
        do_task.do_channels.add_do_chan(f"{device_name}/port1/line3")

        do_task.write([False,False])
        time.sleep(0.1)
        do_task.write([True,True])

    

if __name__ == "__main__":
    initialize_daq_outputs_zero()
