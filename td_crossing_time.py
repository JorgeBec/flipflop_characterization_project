import numpy as np

def find_crossing_time(time1, voltages1, time2, voltages2,type_test):
    """
    Find the time difference between the first threshold crossings (50% amplitude) of two waveforms.
    """
    threshold1 = (np.max(voltages1) / 2)
    print(f"Threshold ch1: {threshold1:.3f} V")

    threshold2 = (np.max(voltages2) / 2)
    print(f"Threshold ch2: {threshold2:.3f} V")

    if type_test == "1": # High to Low
        cross1 = None
        for i in range(len(voltages1)):
            if voltages1[i] <= threshold1:
                cross1 = time1[i]
                print(cross1)
                break  # Stop at first crossing

        cross2 = None
        for i in range(len(voltages2)):
            if voltages2[i] <= threshold2:
                cross2 = time2[i]
                print(cross2)
                break  # Stop at first crossing
        
    elif type_test == "2": # Low to High
        cross1 = None
        for i in range(len(voltages1)):
            if voltages1[i] <= threshold1:
                cross1 = time1[i]
                print(cross1)
                break  # Stop at first crossing

        cross2 = None
        for i in range(len(voltages2)):
            if voltages2[i] >= threshold2:
                cross2 = time2[i]
                print(cross2)
                break  # Stop at first crossing



    crossing_time = cross2 - cross1
    print(f"Propagation delay: {crossing_time * 1e9:.2f} ns")
    return crossing_time




