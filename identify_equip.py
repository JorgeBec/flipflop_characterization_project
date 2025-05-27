import pyvisa
import time

def listar_dispositivos_conectados():
    rm = pyvisa.ResourceManager()
    dispositivos = rm.list_resources()
    
    time.sleep(1)  # Esperar un segundo para asegurar que la lista esté actualizada
    print("📋 Lista de dispositivos detectados:\n")

    if not dispositivos:
        print("❌ No se detectaron instrumentos.")
        return []

    lista_dispositivos = []

    for resource in dispositivos:
        print(f"➡️ {resource}")
        try:
            inst = rm.open_resource(resource, timeout=3000)
            inst.write_termination = '\n'
            inst.read_termination = '\n'

            idn = inst.query('*IDN?').strip()
            print(f"   ✅ Identificado como: {idn}\n")
            lista_dispositivos.append((resource, idn))
        
        except pyvisa.errors.VisaIOError:
            print("   ⚠️ No respondió a *IDN? (posiblemente no SCPI o puerto ocupado)\n")
            lista_dispositivos.append((resource, "No respondió"))
        
        except Exception as e:
            print(f"   ❌ Error inesperado: {type(e).__name__}: {e}\n")
            lista_dispositivos.append((resource, f"Error: {e}"))

    return lista_dispositivos

# Ejecutar función
dispositivos = listar_dispositivos_conectados()

