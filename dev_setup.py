import pyvisa

def find_instruments():
    rm = pyvisa.ResourceManager()
    devices = rm.list_resources()

    osc = None
    dmm = None
    psu = None
    fg = None

    for device in devices:
        try:
            inst = rm.open_resource(device)
            idn = inst.query("*IDN?").strip()

            if "TEKTRONIX,TDS 1012C-EDU" in idn:
                osc = inst
            elif "FLUKE, 45" in idn:
                dmm = inst
            elif "Siglent Technologies,SPD3303X-E" in idn:
                psu = inst
            elif "GW INSTEK,AFG-2005" in idn:
                fg = inst
        except Exception as e:
            print(f"Error accessing {device}: {e}")
            continue

    return osc, dmm, psu, fg
