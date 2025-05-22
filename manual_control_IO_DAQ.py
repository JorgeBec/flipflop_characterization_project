import pyvisa
import time
import re
import nidaqmx
from nidaqmx.constants import AcquisitionType

# ------------------- Generador GW Instek -------------------

def detect_and_configure_gwinstek_afg():
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
                gen.write("SOUR1:APPLy:SQU 1000,5,2.5")
                time.sleep(0.2)
                gen.write("OUTP1 ON")

                print("Generador configurado correctamente.")
                return gen
        except Exception:
            pass
    return None

# ------------------- Fuente de poder SIGLENT -------------------
def detect_siglent_power_supply():
    rm = pyvisa.ResourceManager()
    resources = rm.list_resources()
    for resource in resources:
        try:
            instrument = rm.open_resource(resource)
            idn = instrument.query("*IDN?")
            if "SIGLENT" in idn.upper() and "SPD3303X-E" in idn.upper():
                return instrument
        except Exception:
            pass
    return None

def initialize_power_supply(supply):
    for ch in ["CH1", "CH2"]:
        supply.write(f"{ch}:VOLT 0")
        supply.write(f"{ch}:CURR 0.1")
        supply.write(f"OUTP {ch},OFF")

def configure_channel(supply, channel):
    while True:
        try:
            voltage = float(input(f"Voltaje para {channel} (0 - 7 V): "))
            if 0 <= voltage <= 7:
                supply.write(f"{channel}:VOLT {voltage}")
                supply.write(f"{channel}:CURR 0.1")
                print(f"{channel} configurado a {voltage} V.")
                break
            else:
                print("El voltaje debe estar entre 0 y 7 V.")
        except ValueError:
            print("Entrada inválida. Ingresa un número.")

# ------------------- Control DAQ -------------------
def set_daq_analog_output(channel, voltage):
    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan(
            physical_channel=channel,
            min_val=0.0,
            max_val=5.0
        )
        task.write(voltage)

def set_daq_digital_output(channel, state):
    with nidaqmx.Task() as task:
        task.do_channels.add_do_chan(channel)
        task.write(state)

def configure_daq_signals():
    ao_channels = ['Dev1/ao0', 'Dev1/ao1']
    for ch in ao_channels:
        while True:
            try:
                voltage = float(input(f"Voltaje para {ch} (0-5V): "))
                if 0 <= voltage <= 5:
                    set_daq_analog_output(ch, voltage)
                    break
                else:
                    print("El voltaje debe estar entre 0 y 5 V.")
            except ValueError:
                print("Entrada inválida. Ingresa un número.")

    while True:
        val = input("Valor para P1.0 (0 o 1): ").strip()
        if val in ["0", "1"]:
            set_daq_digital_output("Dev1/port1/line0", bool(int(val)))
            break
        else:
            print("Entrada inválida. Ingresa 0 o 1.")

# ------------------- Lectura multímetro opcional -------------------

def remove_duplicate(measurement):
    """
    Detecta y elimina valores duplicados de medición en la cadena.
    Por ejemplo: "+22.009E+3+22.009E+3" -> "+22.009E+3"
    """
    measurement = measurement.strip()
    pattern = r'[+-]?\d+\.\d+E[+-]?\d+'
    matches = re.findall(pattern, measurement)
    return matches[0] if matches else measurement

def read_voltage_with_fluke45(port='ASRL9::INSTR'):
    """
    Lee y muestra el voltaje medido por el multímetro Fluke 45.
    Asegúrate de que el puerto sea correcto (e.g., ASRL6::INSTR).
    """
    try:
        rm = pyvisa.ResourceManager()
        print("Multímetro conectado en los siguientes puertos:", rm.list_resources())
        instrument = rm.open_resource(port)
        instrument.baud_rate = 9600
        instrument.timeout = 5000

        instrument.write("VOLT")
        print("Cambiado a modo de medición de voltaje...")
        time.sleep(2)

        try:
            val1 = instrument.query("VAL1?").strip()
        except Exception as e:
            print("Error leyendo VAL1?:", e)

        try:
            meas1 = instrument.query("MEAS1?").strip()
            voltage = remove_duplicate(meas1)
            print(f"Voltaje medido por el multímetro Fluke 45: {voltage} V")
            return voltage
        except Exception as e:
            print("Error leyendo MEAS1?:", e)
            return None

    except Exception as e:
        print("Error conectando con el multímetro:", e)
        return None


# ------------------- Main -------------------
if __name__ == "__main__":
    function_generator = detect_and_configure_gwinstek_afg()

    power_supply = detect_siglent_power_supply()
    if power_supply:
        initialize_power_supply(power_supply)
        configure_channel(power_supply, "CH1")  # Solo VCC
        power_supply.write("OUTP CH1,ON")
        
        configure_daq_signals()

        read_voltage_with_fluke45()  # Opcional

    else:
        print("No se detectó la fuente de poder SIGLENT.")
