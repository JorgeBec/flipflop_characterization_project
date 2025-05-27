import pyvisa
import nidaqmx
from nidaqmx.constants import LineGrouping
import time
import re
from tabulate import tabulate

Canal_0 = [False, False, False] 
Canal_1 = [False, False, True]  
Canal_2 = [False, True, False] 
Canal_3 = [False, True, True] 
Canal_4 = [True, False, False] 
Canal_5 = [True, False, True] 
Canal_6 = [True, True, False]
Canal_7 = [True, True, True]

# --------------------------------- Daq-------------------------------------------
with nidaqmx.Task() as task_ao, nidaqmx.Task() as task_do, nidaqmx.Task() as do_task:
    task_ao.ao_channels.add_ao_voltage_chan("Dev2/ao0", min_val=0.0, max_val=5.0)
    task_ao.ao_channels.add_ao_voltage_chan("Dev2/ao1", min_val=0.0, max_val=5.0)

    task_do.do_channels.add_do_chan("Dev2/port0/line0:2", line_grouping=LineGrouping.CHAN_PER_LINE) # A B C
    do_task.do_channels.add_do_chan("Dev2/port1/line0") #clr
    do_task.do_channels.add_do_chan("Dev2/port1/line1") #clk

    #---------------------------------------------------Voltage1------------------------------------------
    task_ao.write([5, 0])
    task_do.write(Canal_0)
