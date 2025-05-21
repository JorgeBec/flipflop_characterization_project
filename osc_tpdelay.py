import pyvisa


rm = pyvisa.ResourceManager()
devices = rm.list_resources()

print("Connected VISA devices:")
for device in devices:
    print(device)

osc = rm.open_resource(devices[0])
print(osc.query("*IDN?")) 