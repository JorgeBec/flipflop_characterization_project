import pyvisa
import numpy as np
import matplotlib.pyplot as plt

# Inicializa la conexión con el Resource Manager
rm = pyvisa.ResourceManager()

# Lista todos los recursos disponibles
recursos = rm.list_resources()
print("Dispositivos encontrados:")
for i, recurso in enumerate(recursos):
    print(f"{i+1}: {recurso}")

# Intenta identificar cada dispositivo
print("\nIdentificando cada dispositivo con *IDN?...*")
for recurso in recursos:
    try:
        dispositivo = rm.open_resource(recurso)
        idn = dispositivo.query("*IDN?")
        print(f"{recurso} -> {idn.strip()}")
        dispositivo.close()
    except Exception as e:
        print(f"{recurso} -> No responde a *IDN? ({e})")